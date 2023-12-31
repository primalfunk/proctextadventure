from .game_objects import Armor, Character, Healing, Key, Lock, Player, Room , Weapon 
import itertools
import logging
import numpy as np
import random

class GameMap:
    def __init__(self, rooms_data, grid_width, grid_height, data_loader, player=None):
        self.data_loader = data_loader
        self.max_retries = 10
        self.target_rooms = grid_width * grid_height
        self.rooms = []
        self.room_clusters = {}
        self.rooms_data = rooms_data
        self.player = player if player else Player()
        self.player_start_room = None
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.dx = {"north": 0, "south": 0, "east": 1, "west": -1}
        self.dy = {"north": -1, "south": 1, "east": 0, "west": 0}
        self.directions = {
        "north": (0, -1, "south"),
        "south": (0, 1, "north"),
        "east": (1, 0, "west"),
        "west": (-1, 0, "east"),
        }
        self.room_to_cluster_map = {}
        self.mst = set()
        self.frontier_positions = set()
        self.adj_cycle = self.init_cycle("adjectives")
        self.name_cycle = self.init_cycle("name")
        self.scenery_cycle = self.init_cycle("scenery")
        self.atmosphere_cycle = self.init_cycle("atmosphere")
        self.room_dict = {(x, y): None  for x in range(grid_width) for y in range(grid_height)}
        self.treasure = self.data_loader.treasure

    def init_cycle(self, field):
        all_items = [data[field] for data in self.rooms_data]
        flattened_items = [item for sublist in all_items for item in sublist]
        random.shuffle(flattened_items)
        return itertools.cycle(flattened_items)

    def is_adjacent_position(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == 1

    def add_placeables(self, all_rooms, enemy_count):
        # This function creates an infinite cycle from a list.
        def create_cycle_from_list(item_list):
            random.shuffle(item_list)
            return itertools.cycle(item_list)

        placeable_methods = [
            self.generate_key,
            self.generate_lock,
            self.generate_weapon,
            self.generate_armor,
        ] + [self.generate_character] * (enemy_count + 1)

        game_data = {
            "key_item": create_cycle_from_list(self.data_loader.genre["elements"]["puzzle_items"].copy()),
            "lock_item": create_cycle_from_list(self.data_loader.genre["elements"]["puzzle_items"].copy()),
            "weapon": create_cycle_from_list(self.data_loader.genre["elements"]["weapons"].copy()),
            "armor": create_cycle_from_list(self.data_loader.genre["elements"]["armor"].copy()),
        }
        self.character_cycle = create_cycle_from_list(self.data_loader.genre["elements"]["characters"])
        
        placeable_data = [
            next(game_data["key_item"]),
            next(game_data["lock_item"]),
            next(game_data["weapon"]),
            next(game_data["armor"]),
        ]
        start_level_diff = max(1, self.player.level - 5)
        end_level_diff = self.player.level + 5
        level_diffs = list(range(start_level_diff, end_level_diff))
        full_weights = [6 - abs(i) for i in range(-5, 6)]
        weights = full_weights[(start_level_diff - 1):(end_level_diff - 1)]
        for _ in range(enemy_count):
            placeable_data.append(self.generate_character_data(weights, level_diffs, True))
        
        
        placeable_data.append(self.generate_character_data(weights, level_diffs, False))
        placeable_attributes = ["key_item", "lock_item", "weapon", "armor"]
        placeable_attributes.extend("enemy" for _ in range(enemy_count))
        placeable_attributes.append("ally")
        possible_locations = all_rooms.copy()
        if self.player_start_room in possible_locations:
            possible_locations.remove(self.player_start_room)
        if len(possible_locations) < len(placeable_data):
            raise Exception("Not enough rooms for all placeable items!")
        for method, data, attr in zip(placeable_methods, placeable_data, placeable_attributes):
            room = random.choice(possible_locations)
            placeable = method(*data) if isinstance(data, tuple) else method(data)
            setattr(room, attr, placeable)
            placeable.current_room = room
            possible_locations.remove(room)

    def generate_character_data(self, weights, level_diffs, is_enemy):
        character = next(self.character_cycle)
        level = np.random.choice(level_diffs, p=np.array(weights)/sum(weights))
        return character, level, is_enemy
    
    def add_room(self, room, x, y, cluster_id, last_added_room=None, is_first_room=False):
        self._add_room_to_maps_and_list(room, x, y)
        if is_first_room:
            if cluster_id == 0:
                room.max_connections = 1
            else:
                room.max_connections = 2
        else:
            room.max_connections = 4
        if last_added_room and self._can_connect_to_last_room(room, last_added_room):
            self._connect_rooms(room, last_added_room)
        self._connect_to_existing_room(room)
        self._manage_room_clusters(room, cluster_id)
        self.positions.remove((x, y))
        return room

    def _get_position(self, x, y):
        if x is None or y is None:
            x, y = self.find_free_random_position()
        elif not self.is_position_free(x, y):
            raise Exception(f"Position {x}, {y} is not free.")
        return x, y

    def _set_room_attributes(self, room, x, y, cluster_id):
        room.x = x
        room.y = y
        room.cluster_id = cluster_id
        return room

    def _add_room_to_maps_and_list(self, room, x, y):
        self.room_dict[(x, y)] = room
        self.rooms.append(room)

    def _connect_to_existing_room(self, new_room):
        adjacent_rooms = new_room.get_adjacent_rooms()
        for adj_room in adjacent_rooms:
            if adj_room.cluster_id == new_room.cluster_id:
                if new_room.count_connections() < new_room.max_connections and adj_room.count_connections() < adj_room.max_connections:
                    direction = self.calculate_direction(adj_room, new_room)
                    self.connect_rooms(adj_room, new_room, direction)

    def _connect_room_to_surroundings(self, room):
        new_connections_made = True
        while new_connections_made:
            new_connections_made = False
            adjacent_rooms = room.get_adjacent_rooms()
            for adj_room in adjacent_rooms:
                if self.can_connect_rooms(room, adj_room):
                    direction = self.calculate_direction(room, adj_room)
                    self.connect_rooms(room, adj_room, direction)
                    new_connections_made = True

    def _can_connect_to_last_room(self, room, last_added_room):
        return (
            last_added_room
            and last_added_room.count_connections() < last_added_room.max_connections
            and self.is_adjacent(room, last_added_room)
        )

    def _manage_room_clusters(self, room, cluster_id):
        if cluster_id is not None:
            self._add_room_to_cluster(room, cluster_id)
            self.room_to_cluster_map[room] = cluster_id

    def _add_room_to_cluster(self, room, cluster_id):
        logging.info(f"Adding room to cluster {cluster_id} at {room.x}, {room.y}")
        room.cluster_id = cluster_id
        if cluster_id in self.room_clusters:
            rooms = self.room_clusters[cluster_id]
            rooms.append(room)
            random.shuffle(rooms)
        else:
            self.room_clusters[cluster_id] = [room]

    def calculate_direction(self, room1, room2):
        x1, y1 = room1.grid_position
        x2, y2 = room2.grid_position
        if x1 == x2:
            if y2 < y1:
                return "north"
            else:
                return "south"
        elif y1 == y2:
            if x2 < x1:
                return "west"
            else:
                return "east"
        else:
            raise ValueError("Rooms are not adjacent.")

    def calculate_distance(self, room1, room2):
        if isinstance(room1, Room):
            pos1 = (room1.x, room1.y)
        else:
            pos1 = room1
        if isinstance(room2, Room):
            pos2 = (room2.x, room2.y)
        else:
            pos2 = room2
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        distance = dx + dy
        return distance

    def rooms_are_adjacent(self, room1, room2):
        return abs(room1.x - room2.x) + abs(room1.y - room2.y) == 1

    def can_connect_rooms(self, room1, room2):
        is_already_connected = self.is_connected(room1, room2)
        room1_has_space = room1.count_connections() < room1.max_connections
        room2_has_space = room2.count_connections() < room2.max_connections
        rooms_are_adjacent = self.are_rooms_adjacent(room1, room2)
        return not is_already_connected and room1_has_space and room2_has_space and rooms_are_adjacent
    
    def connect_clusters(self):
        edges = []
        for room1 in self.rooms:
            for room2 in self.rooms:
                if room1 != room2:
                    can_connect = self.can_connect_rooms(room1, room2)
                    if can_connect:
                        distance = self.manhattan_distance(room1, room2)
                        edges.append((distance, room1, room2))
        edges.sort()
        sets = {room: {room} for room in self.rooms}
        for distance, room1, room2 in edges:
            if sets[room1] != sets[room2]:
                direction = self.calculate_direction(room1, room2)
                connect_result = self.connect_rooms(room1, room2, direction)
                if connect_result:
                    union = sets[room1].union(sets[room2])
                    for room in union:
                        sets[room] = union

    def manhattan_distance(self, room1, room2):
        x1, y1 = room1.grid_position
        x2, y2 = room2.grid_position
        return abs(x1 - x2) + abs(y1 - y2)

    def are_rooms_adjacent(self, room1, room2):
        dx = abs(room1.x - room2.x)
        dy = abs(room1.y - room2.y)
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def connect_rooms(self, room1, room2, direction):
        if not self.is_adjacent(room1, room2):
            return False
        opposite = self.opposite_direction(direction)
        if self.is_connected(room1, room2):
            return False
        room1.connected_rooms[direction] = room2
        room2.connected_rooms[opposite] = room1
        pos1 = (room1.x, room1.y)
        pos2 = (room2.x, room2.y)
        self.room_dict[pos1].connected_rooms[direction] = self.room_dict[pos2]
        self.room_dict[pos2].connected_rooms[opposite] = self.room_dict[pos1]
        return True

    def create_and_place_items(self, all_rooms):
        item_types = ["armor", "weapon", "enemy", "ally", "key_item", "lock_item"]
        possible_locations = all_rooms.copy() 
        possible_locations.remove(self.player_start_room)  
        for item_type in item_types:
            item = self.create_item(item_type)
            room = random.choice(possible_locations)
            room.add_item(item)
            possible_locations.remove(room)

    def create_cluster(self, room_type, cluster_id):
        max_rooms = 10
        min_rooms = 7   
        self.frontier_positions.clear()
        frontier_source_rooms = {}
        start_position = self.find_free_random_position(start_center=cluster_id == 0)
        if start_position is None:
            logging.error("Failed to find a free random position.")
            return False
        start_room = self.generate_room(room_type, *start_position)
        if cluster_id == 0:
            start_room.max_connections = 1
        elif cluster_id > 0:
            start_room.max_connections = 2
        self.add_room(start_room, *start_position, cluster_id, is_first_room=True)
        initial_frontier_positions = self.get_free_adjacent_positions(start_position, cluster_id)
        self.frontier_positions = list(initial_frontier_positions)
        for pos in initial_frontier_positions:
            frontier_source_rooms[pos] = start_room
        rooms_in_cluster = 1
        cluster_target = random.randint(min_rooms, max_rooms)
        while self.frontier_positions and rooms_in_cluster < cluster_target:
            position_index = random.randrange(len(self.frontier_positions))
            position = self.frontier_positions.pop(position_index)
            last_added_room = frontier_source_rooms.pop(position)
            new_room = self.generate_room(room_type, *position)
            new_room.max_connections = 4
            self.add_room(new_room, *position, cluster_id)
            last_added_room = new_room
            rooms_in_cluster += 1
            new_positions = self.get_free_adjacent_positions(position, cluster_id)
            self.frontier_positions.extend(new_positions)
            for pos in new_positions:
                frontier_source_rooms[pos] = last_added_room
            random.shuffle(self.frontier_positions)
        return rooms_in_cluster >= 1
    
    def favor_square_cluster(self, current_pos, visited_positions):
        dx_min = min(pos[0] for pos in visited_positions)
        dx_max = max(pos[0] for pos in visited_positions)
        dy_min = min(pos[1] for pos in visited_positions)
        dy_max = max(pos[1] for pos in visited_positions)
        width = dx_max - dx_min
        height = dy_max - dy_min
        if width > height:
            favored_directions = ["north", "south"]
        else:
            favored_directions = ["east", "west"]
        return favored_directions

    def find_free_random_position(self, start_center=False):
        if start_center:
            x, y = self.grid_width // 2, self.grid_height // 2
            if self.is_position_free(x, y):
                return (x, y)
        elif self.frontier_positions:
            for position in random.sample(self.frontier_positions, len(self.frontier_positions)):
                if self.is_position_free(*position):
                    return position
        else:
            free_positions = [pos for pos in self.positions if self.is_position_free(*pos)]
            if free_positions:
                return random.choice(free_positions)
        return None
        
    def generate_key(self, key_data):
        return Key(key_data["key_item"], key_data["lock_item"])

    def generate_lock(self, lock_data):
        return Lock(lock_data["lock_item"], lock_data["key_item"])

    def generate_healing(self, healing_data):
        return Healing(healing_data["type"], healing_data["stats"]["hp"])

    def generate_weapon(self, weapon_data):
        return Weapon(weapon_data["type"], weapon_data["stats"]["damage"], weapon_data["stats"]["accuracy"])

    def generate_armor(self, armor_data):
        return Armor(armor_data["type"], armor_data["stats"]["defp"], armor_data["stats"]["ev"])

    def generate_character(self, character_data, level, is_enemy = True):
        return Character(character_data["type"],
                         level,
                         character_data["stats"]["hp"], 
                         character_data["stats"]["atk"], 
                         character_data["stats"]["defp"], 
                         character_data["stats"]["acc"], 
                         character_data["stats"]["ev"],
                         is_enemy)

    def generate_game_map(self, rooms_data):
        self.rooms = []
        self.room_clusters = {}
        room_types = [data["type"] for data in rooms_data]
        self.rooms_data = rooms_data
        random.shuffle(room_types)
        logging.info(f"Room types selected are: {room_types}")
        self.generate_positions()
        self.cluster_roots = []
        room_type_cycle = itertools.cycle((room_types))
        all_rooms = []
        cluster_id = 0
        while self.is_map_full is False:
            logging.debug(f"Current state of is_map_full: {self.is_map_full}")
            room_type = next(room_type_cycle)
            logging.info(f"Attempting to create cluster {cluster_id} with room type {room_type}")
            cluster_created = self.create_cluster(room_type, cluster_id)
            logging.info(f"Cluster creation result: {cluster_created}")
            cluster_id += 1
            if not cluster_created:
                logging.info(f"Failed to create cluster {cluster_id-1}, skipping to next.")
                continue
            cluster_rooms = self.room_clusters[cluster_id-1]
            if cluster_id == 1 and cluster_rooms:
                logging.info(f"Setting player start room: {cluster_rooms[0].x}, {cluster_rooms[0].y}")
                self.set_player_start_room(cluster_rooms[0])
                logging.info(f"The player's start room is: {self.player_start_room.x}, {self.player_start_room.y}")
            all_rooms.extend(cluster_rooms)
            for room in cluster_rooms:
                self._connect_room_to_surroundings(room)
            if self.is_map_full:
                break
        self.connect_clusters()
        self.add_placeables(all_rooms, enemy_count=3)
        logging.info(self.render_fancy_map())
        if self.is_map_full:
            for room in all_rooms:
                if room.key_item:
                    print(f"Room at {room.x}, {room.y} has {room.key_item.name}")
                if room.lock_item:
                    print(f"Room at {room.x}, {room.y} has {room.lock_item.name}")
                if room.ally:
                    print(f"Room at {room.x}, {room.y} has {room.ally.name}")
                if room.enemy:
                    print(f"Room at {room.x}, {room.y} has {room.enemy.name}")
                if room.weapon:
                    print(f"Room at {room.x}, {room.y} has {room.weapon.name}")
                if room.armor:
                    print(f"Room at {room.x}, {room.y} has {room.armor.name}")
            return True
        logging.error("Game map generation failed.")
        return False

    def generate_positions(self):
        positions = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height)]
        random.shuffle(positions)
        self.positions = positions
    
    def generate_room(self, room_type, x, y):
        adjective = next(self.adj_cycle).title()
        name = next(self.name_cycle).title()
        scene = next(self.scenery_cycle)
        atmos = next(self.atmosphere_cycle)
        unique_name = f'{adjective} {name}'
        unique_description = f'{scene} {atmos}'
        room = Room(room_type, unique_name, unique_description, x, y)
        return room

    def get_free_adjacent_positions(self, position, cluster_id):
        x, y = position
        possible_positions = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        random.shuffle(possible_positions)
        return [pos for pos in possible_positions if self.is_position_in_map(pos) and self.is_position_free(*pos) and pos not in self.frontier_positions and self.is_adjacent_to_cluster(pos, cluster_id)]
    
    def is_adjacent_to_cluster(self, position, cluster_id):
        x, y = position
        possible_positions = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return any(self.room_dict.get(pos) is not None and 
           self.room_dict.get(pos).cluster_id == cluster_id for pos in possible_positions)
    
    def is_position_in_map(self, position):
        x, y = position
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    def get_direction(self, room1, room2):
        dx = room2.x - room1.x
        dy = room2.y - room1.y
        if dx == 1 and dy == 0:
            return "east"
        elif dx == -1 and dy == 0:
            return "west"
        elif dx == 0 and dy == 1:
            return "south"
        elif dx == 0 and dy == -1:
            return "north"
        else:
            return "not connected"
    
    def is_adjacent(self, room1, room2):
        return (
            (abs(room1.x - room2.x) == 1 and room1.y == room2.y) or
            (abs(room1.y - room2.y) == 1 and room1.x == room2.x)
        )
    
    def is_connected(self, room1, room2):
        return room2 in room1.connected_rooms.values() and room1 in room2.connected_rooms.values()
    
    @property
    def is_map_full(self):
        logging.info(f"Checked if the map was full. There are {len(self.positions)} empty positions left in the grid.")
        return len(self.positions) == 0

    def is_position_free(self, x, y):
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return False
        for room in self.rooms:
            if room.x == x and room.y == y:
                return False
        return True

    @staticmethod
    def opposite_direction(direction):
        opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}
        return opposites.get(direction, None)
    
    def set_player_start_room(self, room):
        self.player_start_room = room

    def render_fancy_map(self):
        rendered_map = [[' ' for _ in range(2*self.grid_width)] for _ in range(2*self.grid_height)]
        for room in self.rooms:
            if room is None:
                logging.warning(f"Room at position ({room.x}, {room.y} is None)")
            if room is not None:
                if room == self.player.current_room:
                    rendered_map[2*room.y][2*room.x] = 'P'
                elif room.enemy:
                    rendered_map[2*room.y][2*room.x] = 'E'
                elif room.weapon:
                    rendered_map[2*room.y][2*room.x] = 'W'
                elif room.armor:
                    rendered_map[2*room.y][2*room.x] = 'A'
                elif room.key_item:
                    rendered_map[2*room.y][2*room.x] = 'K'
                elif room.lock_item:
                    rendered_map[2*room.y][2*room.x] = 'L'
                elif room.ally:
                    rendered_map[2*room.y][2*room.x] = 'Y'
                else:
                    rendered_map[2*room.y][2*room.x] = 'X'
                for direction, connected_room in room.connected_rooms.items():
                    if connected_room is not None:
                        if direction == "north" and 2*room.y - 1 >= 0:
                            rendered_map[2*room.y - 1][2*room.x] = '|'
                        elif direction == "south" and 2*room.y + 1 < len(rendered_map):
                            rendered_map[2*room.y + 1][2*room.x] = '|'
                        elif direction == "west" and 2*room.x - 1 >= 0:
                            rendered_map[2*room.y][2*room.x - 1] = '-'
                        elif direction == "east" and 2*room.x + 1 < len(rendered_map[0]):
                            rendered_map[2*room.y][2*room.x + 1] = '-'
                    else:
                        pass
        return '\n'.join([''.join(row) for row in rendered_map])

    def render_map(self):
        rendered_grid = [[' ']*self.grid_width for _ in range(self.grid_height)]
        for (x, y), room in self.room_dict.items():
            if room is not None:
                rendered_grid[y][x] = 'X'
        rendered_map = '\n'.join(''.join(row) for row in rendered_grid)
        return rendered_map

