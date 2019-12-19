#  Copyright 2015-2019 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class Pet:

    def __init__(self, age=None, name=None):
        self.age = age
        self.name = name

    def __str__(self):
        return f'This is my pet {self.name} and it is {self.age} years old.'


class Person:

    def __init__(self, name=None, age=None, salary=None, pet=None):
        self.name = name
        self.age = age
        self.salary = salary
        self.pet = pet

    def __str__(self):
        return f'My name is {self.name} and I am {self.age}. {self.pet}'
