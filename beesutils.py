import sys
import os
import logging
from typing import List, Tuple, Dict
from enum import Enum
import random
from collections import deque
from datetime import datetime
import threading


#########################################################################

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


def logging_initializer(level: str, log_file: str = None) -> None:
    """ Sets the logging level, allows you to specify an optional log file.
    Choose from: DEBUG, INFO, WARNING, ERROR, CRITICAL (case is not sensitive)
    usage: logging_initializer("DEBUG", "log_file.log") """

    format: str = "%(asctime)s - %(levelname)s - %(message)s"      #   <-- Change this to modify the log format

    try:
        logger_level = LogLevel[level.upper()].value        # Convert the string level to an enum member and get its value
        if log_file:
            logging.basicConfig(level=logger_level, format=format, filename=log_file)
        else:
            logging.basicConfig(level=logger_level, format=format)
    except KeyError:
        raise ValueError(f"Invalid logging level: {level}. Choose from {list(LogLevel.__members__.keys())}")

    """Extra notes: __members__ is a dictionary of the members of the Enum class.
    One of the many things you can do with an Enum. """


def log_level_toggle() -> None:
    """ Toggle the logging level between DEBUG and INFO. """

    current_level: int = logging.getLogger().getEffectiveLevel()
    logger_level: str = log_level_names[current_level]
    print(color(f"Logging level change requested. Current level is: {logger_level}", "cyan"))

    if current_level == 10:
        logging.getLogger().setLevel(20)
        logging.info(color("Logging level set to INFO.", "green"))
    if current_level == 20:
        logging.getLogger().setLevel(10)
        logging.debug(color("Logging level set to DEBUG.", "green"))


def color(text: str, color: str = "yellow") -> str:
    """Wrap text with the given ANSI color code. Default is yellow if no color is specified. """

    ANSI = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "orange": "\033[38;5;208m",
        "reset": "\033[0m",
    }

    color = color.lower()

    return f"{ANSI[color]}{text}{ANSI['reset']}"



def get_size(obj: object) -> int:
    """Get the size of object in megabytes."""

    size_bytes = sys.getsizeof(obj)
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    return size_mb



def print_env_variables(custom_variables: List[str] = None) -> None:
    """ Pass no arguments to print the default list of environment variables.
    Pass "all" to print all environment variables. Pass a list of strings to print specific variables. """

    if isinstance(custom_variables, str) and custom_variables.lower() == "all":
        variables_to_print = os.environ.keys()

    elif isinstance(custom_variables, list):
        variables_to_print = custom_variables
            
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
        raise ValueError("Invalid argument. Pass 'all' to print all environment variables, or a list of strings to print specific variables.")

    print(color(f"Current working directory: {os.getcwd()}  |  Platform: {sys.platform}", "cyan"))
    for key in variables_to_print:
        if key in os.environ:
            print(color(f"{key} is {os.environ[key]}", "cyan"))
        else:
            print(color(f"{key} is not in the environment variables.", "red"))


def set_current_dir() -> None:
    """ This sets the working directory to the directory of the script."""


    current_directory: str = os.getcwd()
    print(color(f"Current working directory: {current_directory}", "cyan"))

    # Set the new working directory to the directory of the script
    new_working_dir: str = os.path.dirname(__file__)
    os.chdir(new_working_dir)
    print(color(f"NEW WORKING DIR: {new_working_dir}", "cyan"))



def timestamp() -> datetime:
    """ Return the raw timestamp with datetime.now().
        timestamp = beesutils.timestamp() """
    
    try:
        the_time = datetime.now()
    except Exception as e:
        logging.error(f"Error getting timestamp: {e}")

    return the_time


def elapsed_calc(start_time: float) -> float:
    """ takes a timestamp and returns the elapsed time since then.
    elapsed_time = beesutils.elapsed_calc(timestamp) """

    logging.debug(f"start_time = {start_time}")

    end_time: float = timestamp()
    logging.debug(f"end_time = {end_time}")

    elapsed_time: float = end_time - start_time
    logging.debug(color(f"elapsed_time = {elapsed_time}"))

    return elapsed_time


def format_elapsed(elapsed_time: float) -> str:
    """ Takes the result of elapsed_calc and returns a formatted string.
    formatted_time = beesutils.format_elapsed(elapsed_time) """

    days = elapsed_time.days                            # This is not used but here in case you want to add it
    seconds = elapsed_time.seconds
    microseconds = elapsed_time.microseconds            # Also not used

    # Convert the total seconds into hours, minutes, and remaining seconds
    hours, remainder = divmod(seconds, 3600)            
    minutes, seconds = divmod(remainder, 60) 

    # Format the elapsed time as a string
    formatted_time = f"{minutes:01} minutes and {seconds:02} seconds."

    return formatted_time




def thread_runner(target) -> None:
    """ Runs a function that you pass into it in a separate thread."""

    threadded = threading.Thread(target=target)
    threadded.daemon = True    # daemon threads are killed when the main program exits
    threadded.start()

    logging.debug(color(f"threadded.is_alive() = {threadded.is_alive()}"))


def count_lines_of_code(file_path, remove_comments=False):
    """Count the number of non-blank lines in a file. Optionally remove comments."""

    non_blank_line_count = 0        
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:                               # Check if the line is not blank
            if remove_comments:
                if not stripped_line.startswith('#'):
                    non_blank_line_count += 1
            else:
                non_blank_line_count += 1
    
    # Return the count of non-blank lines
    return non_blank_line_count

    # # Example usage:
    # file_path = 'your_module.py'
    # num_lines = count_lines_without_blanks(file_path, True)
    # print(f'Number of non-blank lines in {file_path}: {num_lines}')
    



def list_files(directory: str, extension: str = None) -> List[str]:
    """List files in a directory with an optional extension filter. Returns a list of strings. """

    files = os.listdir(directory)
    if extension:
        files = [file for file in files if file.endswith(extension)]
    return files