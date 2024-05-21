import sys
import os
import logging
from typing import List, Tuple, Dict
from enum import Enum
import random
from collections import deque
from datetime import datetime
import threading


"""
ANSI color codes:
\033[31m - Red
\033[32m - Green
\033[33m - Yellow
\033[34m - Blue
\033[0m - Reset

List of functions in this file. Try to keep this up to date.

- logging_initializer
- log_level_toggle
- get_size
- print_env_variables
- set_current_dir
- timestamp
- elapsed_calc
- format_elapsed
- thread_runner
- read_file
- write_file
- list_files

"""

# this is just for easy display of the log levels in the toggle function
log_level_names = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL"
}


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class BeesUtils:
    """ This class contains all of Bee's utility functions."""
        

    @staticmethod
    def logging_initializer(level: str, log_file: str = None) -> None:
        """ Sets the logging level, allows you to specify a log file.
        Choose from: DEBUG, INFO, WARNING, ERROR, CRITICAL (case is not sensitive)"""

        format: str = "%(asctime)s - %(levelname)s - %(message)s"

        try:
            logger_level = LogLevel[level.upper()].value        # Convert the string level to an enum member and get its value
            if log_file:
                logging.basicConfig(level=logger_level, format=format, filename=log_file)
            else:
                logging.basicConfig(level=logger_level, format=format)
        except KeyError:
            raise ValueError(f"Invalid logging level: {level}. Choose from {list(LogLevel.__members__.keys())}")

        """Extra notes: __members__ is a dictionary of the members of the Enum class.
        One of the many things you can do with an Enum is iterate over its members. """

    def log_level_toggle() -> None:
        """ Toggle the logging level between DEBUG and INFO. """

        current_level: int = logging.getLogger().getEffectiveLevel()
        logger_level: str = log_level_names[current_level]
        print(f"Logging level change requested. Current level is: {logger_level}")

        if current_level == 10:
            logging.getLogger().setLevel(20)
            logging.info("Logging level set to INFO.")
        if current_level == 20:
            logging.getLogger().setLevel(10)
            logging.debug("Logging level set to DEBUG.")


    @staticmethod
    def get_size(obj: object) -> int:
        """Get the size of object in megabytes."""

        size_bytes = sys.getsizeof(obj)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        return size_mb
    
    
    @staticmethod
    def print_env_variables(custom_variables: List[str] = None) -> None:
        """ Pass no arguments to print the default list of environment variables.
        Pass "all" to print all environment variables. Pass a list of strings to print specific variables. """

        if custom_variables == "all":
            variables_to_print = os.environ.keys()
            
        elif custom_variables is None:
            variables_to_print = [
                "NUMBER_OF_PROCESSORS",
                "OS",
                "PROCESSOR_IDENTIFIER",
                "USERDOMAIN_ROAMINGPROFILE",
                "USERDOMAIN",
                "USERNAME",
            ]
        else:
            variables_to_print = custom_variables

        print("\033[36m", end="")   ## ANSI ON (cyan)
        print(f"Current working directory: {os.getcwd()}  |  Platform: {sys.platform}")

        for key in variables_to_print:
            if key in os.environ:
                print("\033[36m", end="")   ## ANSI ON (cyan)
                print(f"{key} is {os.environ[key]}")
                ## Remember that os.environ[key] is the same as saying 'the value associated with that key'.
            else:
                print("\033[31m", end="")   ## ANSI ON (red)
                print(f"{key} is not in the environment variables.")
        print("\033[0m")    ## ANSI OFF


    @staticmethod
    def set_current_dir() -> None:
        """ This sets the working directory to the directory of the script."""

        current_directory: str = os.getcwd()
        print("Current working directory:", current_directory)

        # Set the new working directory to the directory of the script
        new_working_dir: str = os.path.dirname(__file__)
        os.chdir(new_working_dir)
        print("NEW WORKING DIR:", new_working_dir)
        print("\033[0m")    ## ANSI OFF

    
    @staticmethod
    def timestamp() -> datetime:
        """ Return the raw timestamp with datetime.now().
         timestamp = BeesUtils.timestamp() """
       
        try:
            the_time = datetime.now()
        except Exception as e:
            logging.error(f"Error getting timestamp: {e}")

        return the_time
    
    @staticmethod
    def elapsed_calc(start_time: float) -> float:
        """ takes a timestamp and returns the elapsed time since then.
        elapsed_time = BeesUtils.elapsed_calc(timestamp) """

        logging.debug(f"\033[33m start_time = {start_time} \033[0m")

        end_time: float = BeesUtils.timestamp()
        logging.debug(f"\033[33m end_time = {end_time} \033[0m")

        elapsed_time: float = end_time - start_time
        logging.debug(f"\033[33m elapsed_time = {elapsed_time} \033[0m")

        return elapsed_time
    
    @staticmethod
    def format_elapsed(elapsed_time: float) -> str:
        """ Takes a float and returns a formatted string.
        formatted_time = BeesUtils.format_elapsed(elapsed_time) """
    
        days = elapsed_time.days                            # This is not used but here in case you want to add it
        seconds = elapsed_time.seconds
        microseconds = elapsed_time.microseconds            # Also not used

        # Convert the total seconds into hours, minutes, and remaining seconds
        hours, remainder = divmod(seconds, 3600)            
        minutes, seconds = divmod(remainder, 60) 

        # Format the elapsed time as a string
        formatted_time = f"{minutes:01} minutes and {seconds:02} seconds."

        return formatted_time

    
    
    @staticmethod
    def thread_runner(target) -> None:
        """ Runs a function that you pass into it in a separate thread."""

        threadded = threading.Thread(target=target)
        threadded.daemon = True    # daemon threads are killed when the main program exits
        threadded.start()

        logging.debug(f"\033[33m threadded.is_alive() = {threadded.is_alive()} \033[0m")


    @staticmethod
    def read_file(file_path: str) -> str:
        """Read a file and return its contents."""

        with open(file_path, 'r') as file:
            return file.read()
        

    @staticmethod
    def write_file(data: str, file_path: str) -> None:
        """Write data to a file. Takes two arguments: the data to write followed by file path."""

        with open(file_path, 'w') as file:
            file.write(data)


    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """List files in a directory with an optional extension filter. Returns a list of strings. """

        files = os.listdir(directory)
        if extension:
            files = [file for file in files if file.endswith(extension)]
        return files