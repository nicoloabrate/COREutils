from pydantic import ConfigDict
from pydantic import BaseModel, Field, AliasPath, AliasChoices
from pydantic import PositiveInt, PositiveFloat, NonNegativeFloat
from pydantic import ValidationError, model_validator
from typing import Any, Optional, Dict, List, Union
from coreutils.input.input_model import *

class func_BCs(BaseModel):

    dt: NonNegativeFloat
    variation: NonNegativeFloat


class func_power(BaseModel):

    time: NonNegativeFloat
    value: NonNegativeFloat


class pertBCs(BaseModel):
    which: List[List[PositiveInt]]
    func: Optional[List[Dict[str, func_BCs]]] = None
    filepath: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate(self) -> 'pertBCs':
        if self.func is None and self.filepath is None:
            raise ValueError("Either func or filepath must be provided!")

        if self.func is not None and self.filepath is not None:
            raise ValueError("Only one between func and filepath can be provided!")

        if self.func is not None:
            for shape in self.func:
                for s in shape:
                    if s not in ["step", "linear"]:
                        raise ValueError(f'Unknown {s} entry in func!')

        if self.filepath is not None and len(self.filepath) not in [1, len(self.which)]:
            raise ValueError('Length of which and filepath is not consistent!')

        return self


class perturbBCs_obj(BaseModel):
    massflowrate: Optional[pertBCs] = None
    temperature: Optional[pertBCs] = None
    pressure: Optional[pertBCs] = None


class power_obj(BaseModel):
    mode: str = "channels"
    which: Optional[List[List[PositiveInt]]] = None
    func: Optional[Any] = None
    filepath: Optional[Union[str, List[str]]] = None
    shape_factor: Optional[str] = None
    shape_factors: Optional[str] = None

    @model_validator(mode="after")
    def validate(self) -> 'power_obj':
        mode = self.mode.casefold().replace("-", "_")
        valid_modes = ["channels", "shape", "shape_time"]
        if mode not in valid_modes:
            raise ValueError(f"Unknown power mode {self.mode}!")

        if mode == "channels":
            has_group_profile = self.which is not None and (self.func is not None or self.filepath is not None)
            has_full_file = self.which is None and isinstance(self.filepath, str)
            if not has_group_profile and not has_full_file:
                raise ValueError("channels power mode requires either filepath or which with func/filepath!")
    
        elif mode == "shape":
            if self.shape_factor is None and self.shape_factors is None:
                raise ValueError("shape power mode requires shape_factor or shape_factors!")
            if self.func is None and self.filepath is None:
                raise ValueError("shape power mode requires func or filepath for the total power P(t)!")
            if isinstance(self.filepath, list):
                raise ValueError("shape power mode accepts a single filepath for P(t)!")

        else:
            if not isinstance(self.filepath, str):
                raise ValueError("shape_time power mode requires a filepath!")

        return self
