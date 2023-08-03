from typing import List, Tuple
import asyncio
import aiohttp
import os

import argparse
from argparse import Namespace
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from station import RadioStation, Broadcast

from kolhay import KolHayStation
from kolbarama import KolBaramaStation
import utils

console = Console()

def setup_args() -> Namespace:
   parser = argparse.ArgumentParser(description="A program for downloading radio broadcasts. It's recommended to use a terminal that supports Hebrew (bidi), such as 'Terminal' in Windows, rather than the older 'cmd'.")
   parser.add_argument('-s', '--station', type=utils.parse_string, help="The station index or the station name.", required=False)
   parser.add_argument('-p', '--program', type=utils.parse_string, help="The program index or the program name.", required=False)
   parser.add_argument('-b', '--broadcasts', type=utils.parse_string, help="The specific broadcast or range of broadcasts you wish to download.", required=False)
   parser.add_argument('-y', '--yes', action='store_true', help="Automatically confirm all prompts with 'yes'.", required=False)
   parser.add_argument('-o', '--output', type=str, default=os.getcwd(), help="The destination of downloaded broadcasts.", required=False)
   parser.add_argument('-pr', '--parallel', type=int, default=1, help="Indicates the number of files to be downloaded in parallel.", required=False)
   parser.add_argument('-i', '--index', type=int, default=1, help="Indicates the start index ONLY for display.", required=False)
   return parser.parse_args()

def get_input(prompt: str, arg: str | None = None) -> int | List[int] | str:
   if arg:
      return arg
   else:
      return utils.parse_string(Prompt.ask(console=console, prompt=prompt))
   
def select_station(args: Namespace, stations: List[RadioStation]) -> RadioStation:
   console.print("[bold]The following stations are available:")
   for i, station in enumerate(stations, 1):
      print(f"{i}. {station.name}")
   
   console.print()

   index = get_input("Enter the index of the station", args.station)
   if not isinstance(index, int):
      console.print("Station must be a number.")
      exit(1)

   station: RadioStation = stations[index - 1]
   console.print(f"[green bold]{station.name}[/] chosen!")

   return station

def select_program(args: Namespace, station: RadioStation) -> int | str:
   with console.status("Fetching programs..."):
      program_list = station.load_programs()

   console.print("\n[bold]These programs are available:")
   for i, program in enumerate(program_list, 1):
      console.print(f"{i}. {program}")
   
   console.print()
   selected_program = get_input("Enter the index or the name of the program", args.program)
   if not isinstance(selected_program, (int, str)):
      console.print("Program must be a number index or the program name, not a range.")
      exit(1)

   if isinstance(selected_program, int):
      selected_program -= 1

   return selected_program

def select_broadcasts(args: Namespace, station: RadioStation, program: int | str) ->  Tuple[List[int], List[Broadcast]]:
   with console.status("Fetching broadcasts...") as status:
      broadcast_list = station.load_broadcasts(program, lambda complete, total: status.update(f"Fetch broadcasts... {complete}/{total}"))

   console.print("\n[bold]These broadcasts are available:")
   for i, broadcast in enumerate(broadcast_list, 1):
      console.print(f"{i}. {broadcast.name}")

   selected_broadcasts = get_input("Enter a specific index or a range of broadcasts or '*' for all", args.broadcasts)
   if isinstance(selected_broadcasts, str):
      if selected_broadcasts == "*":
         selected_broadcasts = range(1, len(broadcast_list) + 1)
      else:
         console.print("Broadcast must be a number index or a range, not a name.")
         exit(1)

   if isinstance(selected_broadcasts, int):
      selected_broadcasts = [selected_broadcasts]

   selected_broadcasts = [i - 1 for i in selected_broadcasts]
   return selected_broadcasts, [broadcast_list[i] for i in selected_broadcasts]

def get_output_dir(args: Namespace) -> str:
   output_directory: str = args.output
   if not os.path.isdir(output_directory):
      console.print(f"{output_directory} is not a valid directory.")
      exit(1)
   
   return output_directory

def get_parallel_downloads(args: Namespace) -> int:
   parallel_downloads: int = args.parallel
   if parallel_downloads < 1:
      console.print("'parallel' argument must be greater than 1.")
      exit(1)

   return parallel_downloads

async def download_file(progress: Progress, 
                        session: aiohttp.ClientSession, 
                        broadcast: Broadcast, iteration: int, 
                        display_start_index: int,
                        dest_directory: str) -> None:
   progress_task = progress.add_task(f"{iteration + display_start_index}. {broadcast.name[:25]}")

   filename = f"{str(iteration + display_start_index).zfill(3)} - {utils.sanitize_filename(broadcast.name)}{os.path.splitext(broadcast.url)[1]}"
   dest = os.path.join(dest_directory, filename)
   progress_callback: utils.ProgressCallback = lambda complete, total, progress_task=progress_task: progress.update(progress_task, total=total, completed=complete)

   await utils.download_async(broadcast.url, dest, session, progress_callback)

   progress.remove_task(progress_task)
   console.print(f"[green]Downloaded![/] {broadcast.name}")

async def download_loop(progress: Progress,
                        broadcasts: List[Broadcast], 
                        max_downloads: int,
                        display_start_index: int,
                        dest_directory: str) -> None:
   tasks: List[asyncio.Task[None]] = []

   async with aiohttp.ClientSession() as session:
      for i, broadcast in enumerate(broadcasts):
         if len(tasks) >= max_downloads:
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            tasks.clear()
            tasks.extend(pending)

         task = asyncio.create_task(download_file(progress, session, broadcast, i, display_start_index, dest_directory))
         tasks.append(task)

      await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

def download_broadcasts(broadcasts: List[Broadcast], 
                        dest_directory: str, 
                        parallel_downloads: int, 
                        display_start_index: int) -> None:
   progress = Progress(
      TextColumn("{task.description}"),
      BarColumn(),
      "[progress.percentage]{task.percentage:>3.0f}%",
      "•",
      DownloadColumn(),
      "•",
      TransferSpeedColumn(),
      "•",
      TimeRemainingColumn(),

      console=console
   )

   with progress:
      asyncio.run(download_loop(progress, broadcasts, parallel_downloads, display_start_index, dest_directory))

def main():
   args = setup_args()
   station = select_station(args, [KolHayStation(), KolBaramaStation()])
   program = select_program(args, station)
   selected_broadcasts, broadcasts = select_broadcasts(args, station, program)

   output_dir = get_output_dir(args)
   parallel_downloads = get_parallel_downloads(args)
   display_start_index: int = args.index
   
   if not args.yes:
      prompt_message = (
         f"Are you sure you want to download the following broadcasts: "
         f"{selected_broadcasts[0] + 1} - "
         f"{selected_broadcasts[len(selected_broadcasts) - 1] + 1}?"
      )
      if not Confirm.ask(console=console, prompt=prompt_message):
         console.print("[red bold]The operation has been cancelled.[/]")
         exit()

   console.print()
   download_broadcasts(broadcasts, output_dir, parallel_downloads, display_start_index)

   console.print("[green bold]Done![/]")

if __name__ =="__main__":
   try:
      main()
   except Exception as e:
      console.print(f"[red bold]Error:[/] {e}")