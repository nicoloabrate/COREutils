from pydantic import ConfigDict
from pydantic import BaseModel, Field, AliasPath, AliasChoices
from pydantic import PositiveInt, PositiveFloat, NonNegativeFloat
from pydantic import ValidationError, model_validator
from typing import Optional, Dict, List
from coreutils.input.input_model import *

class func_BCs(BaseModel):

    dt: NonNegativeFloat
    variation: NonNegativeFloat

class pertBCs(BaseModel):
    which: List[List[PositiveInt]]
    func: Optional[List[Dict[str, func_BCs]]] = None
    filepath: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate(self) -> 'pertBCs':
        which = self.which
        if hasattr(self, "func"):

            for shape in self.func:
                for s in shape.keys():
                    if s not in ["step", "linear"]:
                        raise ValueError(f'Unknown {s} entry in func!')
                    

        elif hasattr(self, "filepath"):
            shape = self.filepath
            
        if len(which) != len(shape):
            raise ValueError('Length of lists is not consistent!')
        return self


class perturbBCs_obj(BaseModel):
    massflowrate: Optional[pertBCs] = None
    temperature: Optional[pertBCs] = None
    pressure: Optional[pertBCs] = None
