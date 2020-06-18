import os
import sys
import argparse
from fractions import Fraction
from typing import List, Tuple, Dict, Set
from random import sample, choice, randint
from soadata import DataPropertyTypeRepo, DataPropertyNameRepo, DataClassNameRepo, DataClassRepo, DataClass, DataProperty, DataService, DataServiceNameRepo, DataServiceRepo

if not (sys.version_info.major == 3 and sys.version_info.minor >= 5):
    print("This script requires Python 3.5 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

parser = argparse.ArgumentParser(description = 'Generates a simulation for service oriented architecture')
parser.add_argument("-d", "--datatypes", help="the number of datatypes", required = True)
parser.add_argument("-c", "--classes", help="the number of data classes", required = True)
parser.add_argument("-s", "--services", help="the number of data services", required = True)
parser.add_argument("-rc", "--refclassratio", help="ratio of class with ref vs simple POJO", default = "1/10")
parser.add_argument("-rs", "--refserviceratio", help="ratio of services with ref vs simple POJO", default = "1/2")
parser.add_argument("-p", "--properties", help="the max number of properties per class", required = True)
parser.add_argument("-n", "--names", help="the number of property names", default = "200")
parser.add_argument("-r", "--refratio", help="ratio of ref vs simple types", default = "1/10")
args = parser.parse_args()

MAX_ITEMS_MAGNITUDE = 48 #2^48
MAX_PROCESSING_MAGNITUDE_MICRO_SEC = 27 # 2^27

class Config:
    def __init__(self):
        self.datatype_count = int(args.datatypes)
        self.class_count = int(args.classes)
        self.properties_max = int(args.properties)
        self.property_name_count = int(args.names)
        self.ref_ratio = Fraction(args.refratio)
        self.ref_class_ratio = Fraction(args.refclassratio)
        self.service_count = int(args.services)
        self.ref_service_ratio = Fraction(args.refserviceratio)
    
    def get_ref_class_count(self)->int:
        return int(self.class_count * self.ref_class_ratio)
    
    def get_simple_class_count(self)->int:
        return self.class_count - self.get_ref_class_count()

    def get_ref_service_count(self)->int:
        return int(self.service_count * self.ref_service_ratio)
    
    def get_simple_service_count(self)->int:
        return self.service_count - self.get_ref_service_count()

config = Config()
dataPropertyTypeRepo = DataPropertyTypeRepo()
dataPropertyTypeRepo.add_types_as_str("Bool Int Float DateTime")
dataPropertyTypeRepo.add_types(["Type{}".format(i) for i in range(config.datatype_count)])

dataPropertyNameRepo = DataPropertyNameRepo()
dataPropertyNameRepo.add_names_auto(config.property_name_count)

dataClassNameRepo = DataClassNameRepo()
dataClassRepo = DataClassRepo()
#Generate simple class POJO
for cl in range(config.get_simple_class_count()):
    dataClass = DataClass()
    dataClass.set_name(dataClassNameRepo.add_next_name())
    propertyNames = dataPropertyNameRepo.sample(randint(1, config.properties_max))
    for pname in propertyNames:
        prop = DataProperty()
        prop.set_name(pname)
        prop.set_max_items(randint(1, MAX_ITEMS_MAGNITUDE))
        prop.set_min_items(randint(0, prop.max_items))
        prop.set_datatype(dataPropertyTypeRepo.random_simple_type())
        dataClass.add(prop)
    dataClassRepo.add_dataclass(dataClass)

dataServiceNameRepo = DataServiceNameRepo()
dataServiceRepo = DataServiceRepo()
#Generate simple services
for srv in range(config.get_simple_service_count()):
    dataService = DataService()
    dataService.set_name(dataServiceNameRepo.add_next_name())
    dataService.set_processing_magnitude(randint(1, MAX_PROCESSING_MAGNITUDE_MICRO_SEC)) 
    dataService.set_error_processing_magnitude(randint(1, MAX_PROCESSING_MAGNITUDE_MICRO_SEC))
    dataService.set_error_rate(Fraction(1, 10**randint(2, 6)))
    dataServiceRepo.add_dataservice(dataService)


print(dataPropertyTypeRepo)
print(dataPropertyNameRepo)
print(dataClassRepo)
print(dataServiceRepo)
