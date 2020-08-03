# -*- coding: utf-8 -*-

from csv import DictWriter
import json
import re
from datetime import timedelta
from decimal import Decimal
from sys import exit
from os import path

remaining_time = '1234567890.0987654321'


class DungeonsAndDragons:

    def __init__(self):
        self.dungeons_map = {}
        self.list_location = []
        self.list_location_norm = []
        self.list_monsters = []
        self.list_monsters_norm = []
        self.first_loc = ''
        self.game = True
        self.exp = 0
        self.remaining_time = Decimal(remaining_time)
        self.from_now = 0

    def run(self):
        with open(file='rpg.json', mode='r') as read_file:
            self.dungeons_map = json.load(read_file)
        self.parser_map()
        print('Dungeons & Dragons\n', '-' * 20)
        print(
            f'You need to complete the whole maze in {timedelta (seconds = float (self.remaining_time))} seconds and \n'
            f'type 280 experience points. Points are earned by killing dragons, \ntime isted fighting '
            f'dragons and along the road in the tunnels.')
        while self.game:
            print('=' * 50)
            print(f'You are in {self.name_normalizer(self.first_loc)}')
            print(f'Your experience is {self.exp} and there are {timedelta (seconds = float (self.remaining_time))} '
                  f'seconds left.')
            print(f'It\'s been {timedelta (seconds = float (self.from_now))} seconds.')
            print('Inside you see:')
            self.list_monsters_norm = self.name_normalizer(self.list_monsters)
            for item in self.list_monsters_norm:
                print(f'-- {item}')
            self.list_location_norm = self.name_normalizer(self.list_location)
            for item in self.list_location_norm:
                print(f'-- Tunnel entrance: {item}')
            self.user_choose()
        self.score()

    def parser_map(self):
        for i in self.dungeons_map:
            self.first_loc = i
            for x in self.dungeons_map[self.first_loc]:
                if type(x) == dict:
                    for y in x:
                        self.list_location.append(y)
                else:
                    self.list_monsters.append(x)

    def change_loc(self):
        print('Where we are going?')
        for num, item in enumerate(self.list_location_norm):
            print(f'{num + 1} -- Tunnel entrance: {item}')
        while True:
            try:
                choose = input(">>>")
                time = re.search(pattern=r'tm\d+', string=self.list_location[int(choose) - 1])
                self.remaining_time -= Decimal(time.group()[2:])
                self.from_now += Decimal(time.group()[2:])
                n = self.list_location[int(choose) - 1]
                for item in self.dungeons_map[self.first_loc]:
                    if type(item) == dict:
                        if item.get(n):
                            self.dungeons_map = item
                break
            except (IndexError, ValueError):
                print('Choose the right number')
        self.list_location = []
        self.list_monsters = []
        self.parser_map()

    def user_choose(self):
        while True:
            try:
                if len(self.list_monsters) > 0 and len(self.list_location) > 0:
                    print('Choose an action:\n1.Attack the dragon\n2.Go to another tunnel\n3.Exit')
                    choose = input(">>>")
                    if choose == '1':
                        self.monster_attack()
                        break
                    elif choose == '2':
                        self.change_loc()
                        break
                    elif choose == '3':
                        self.game = False
                        break
                    else:
                        raise RuntimeError
                elif len(self.list_monsters) == 0 and len(self.list_location) > 0:
                    print('Choose an action:\n1.Go to another tunnel\n2.Exit')
                    choose = input(">>>")
                    if choose == '1':
                        self.change_loc()
                        break
                    elif choose == '2':
                        self.game = False
                        break
                    else:
                        raise RuntimeError
                elif len(self.list_location) == 0 and len(self.list_monsters) > 0:
                    print('Choose an action:\n1.Attack the dragon\n2.Exit')
                    choose = input(">>>")
                    if choose == '1':
                        self.monster_attack()
                        break
                    elif choose == '2':
                        self.game = False
                        break
                    else:
                        raise RuntimeError
                else:
                    print('Game over!')
                    self.score()
            except RuntimeError:
                print('Choose the right number')

    def monster_attack(self):
        choose = None
        while choose != '0':
            try:
                print('Whom are we hitting?')
                for num, monster in enumerate(self.list_monsters_norm):
                    print(f'{num + 1} -- {monster}')
                if len(self.list_location) != 0:
                    print('0 -- or are we running away?')
                choose = input(">>>")
                if choose == '0':
                    self.change_loc()
                else:
                    monster_exp = re.search(pattern=r'exp\d+', string=self.list_monsters[int(choose) - 1])
                    time = re.search(pattern=r'tm\d+', string=self.list_monsters[int(choose) - 1])
                    self.remaining_time -= Decimal(time.group()[2:])
                    self.from_now += Decimal(time.group()[2:])
                    self.exp += int(monster_exp.group()[3:])
                    self.list_monsters.pop(int(choose) - 1)
                    print("Dragon slain!")
                    if len(self.list_monsters) > 0:
                        print(f"Your experience {self.exp} has passed {timedelta(seconds=float(self.from_now))} "
                              f"and there are {timedelta (seconds = float (self.remaining_time))} seconds left.")
                    if len(self.list_monsters) == 0:
                        if len(self.list_location) == 0:
                            self.game = False
                        choose = '0'
            except (IndexError, ValueError):
                print('Choose the right number')

    def score(self):
        print('---Scoring---')
        if self.exp > 279 and self.remaining_time > 0:
            print('HOORAY! You won!')
            self.cvs_write()
        else:
            print('Alas you lost.')
        print(f'Experience earned - {self.exp}')
        print(f'You walked through the dungeon {timedelta(seconds=float(self.from_now))}')
        exit()

    def cvs_write(self):
        print('What your name?')
        name = input('>>>')
        field_names = ['name', 'current_location', 'current_experience', 'current_date']
        file_name = 'dungeon.csv'
        cvs_line = {field_names[0]: name, field_names[1]: self.first_loc, field_names[2]: self.exp, field_names[3]:
            timedelta(seconds=int(self.from_now))}
        if not path.exists(file_name):
            with open(file_name, 'w', newline='') as out_cvs:
                writer = DictWriter(out_cvs, delimiter=',', fieldnames=field_names)
                writer.writeheader()
        with open(file_name, 'a', newline='') as out_cvs:
            writer = DictWriter(out_cvs, delimiter=',', fieldnames=field_names)
            writer.writerow(cvs_line)

    def name_normalizer(self, list_before):
        list_after = []
        if len(list_before) == 0:
            return list_before
        if re.search(pattern=r'Mob', string=list_before[0]):
            for i, string in enumerate(list_before):
                monster_exp = re.search(pattern=r'exp\d+', string=string)
                time = re.search(pattern=r'tm\d+', string=string)
                if len(list_before) > 2:
                    list_after.append(f'The Dragon {(i + 1)}: Experience +{monster_exp.group()[3:]} Time '
                                  f'+{timedelta(seconds=float(time.group()[2:]))} seconds.')
                else:
                    list_after.append(f'The Dragon: Experience +{monster_exp.group()[3:]} Time '
                                      f'+{timedelta(seconds=float(time.group()[2:]))} seconds.')
            return list_after
        elif re.search(pattern=r'Boss', string=list_before[0]):
            for i, string in enumerate(list_before):
                monster_exp = re.search(pattern=r'exp\d+', string=string)
                time = re.search(pattern=r'tm\d+', string=string)
                if len(list_before) > 2:
                    list_after.append(f'Giant Dragon {(i + 1)}: Experience +{monster_exp.group()[3:]} Time '
                                  f'+{timedelta(seconds=float(time.group()[2:]))} seconds.')
                else:
                    list_after.append(f'Giant Dragon: Experience +{monster_exp.group()[3:]} Time '
                                      f'+{timedelta(seconds=float(time.group()[2:]))} seconds.')
            return list_after
        elif re.search(pattern=r'B\d', string=list_before[0]):
            for string in list_before:
                time = re.search(pattern=r'tm\d+', string=string)
                num = re.search(pattern=r'\d', string=string)
                list_after.append(f'Bonus Tunnel {num.group()} Time +{timedelta(seconds=float(time.group()[2:]))}'
                                  f' seconds.')
            return list_after
        elif type(list_before) == str:
                num = re.search(pattern=r'\d+', string=list_before)
                list_after = f'tunnel {num.group()}'
                return list_after
        else:
            for string in list_before:
                time = re.search(pattern=r'tm\d+', string=string)
                num = re.search(pattern=r'\d+', string=string)
                list_after.append(f'{num.group()} Time +{timedelta(seconds=float(time.group()[2:]))} seconds.')
            return list_after


if __name__ == '__main__':
    game = DungeonsAndDragons()
    game.run()
