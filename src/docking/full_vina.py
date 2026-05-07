from pathlib import Path
from string import Template
import os

from wrappers.vina_prep import PrepareLigandWrapper, PrepareReceptorWrapper, VinaWrapper
from config_schema import RootConfig


class FullVinaWorkFlow:
    pass