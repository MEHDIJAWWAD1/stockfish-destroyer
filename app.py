import streamlit as st
import chess
import chess.engine
import html
import math
import random
import shutil
import time
import os
import glob

st.set_page_config(page_title="Asymmetric Army Chess vs Stockfish", layout="wide")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if os.name == "nt":
    found_exes = sorted(glob.glob(os.path.join(APP_DIR, "stockfish*.exe")))
    STOCKFISH_PATH = found_exes[0] if found_exes else os.path.join(APP_DIR, "stockfish.exe")
else:
    system_paths = [
        shutil.which("stockfish"),
        "/usr/games/stockfish",
        "/usr/bin/stockfish",
    ]
    STOCKFISH_PATH = next(
        (path for path in system_paths if path and os.path.isfile(path)),
        os.path.join(APP_DIR, "stockfish"),
    )
ARMIES = {
    1:  {"name": "1. Medieval Siege (Video)", "desc": "Pawns sandwich-kill, Knights have armor, Queens spread plague.", "p": "pike", "n": "templar", "b": "cavalry", "r": "catapult", "q": "plague", "k": "plague"},
    2:  {"name": "2. Undead Horde", "desc": "Captured White pawns respawn on rank 2; Queen raises dead enemies.", "p": "undead", "n": "trample", "b": "sniper", "r": "broadside", "q": "necromancer", "k": "shield"},
    3:  {"name": "3. Spartan Phalanx", "desc": "Pawns cannot be captured from the front; Rooks stun adjacent foes.", "p": "phalanx", "n": "hit_and_run", "b": "cavalry", "r": "stun", "q": "aura_kill", "k": "aura_kill"},
    4:  {"name": "4. Assassin Guild", "desc": "Knights turn invisible; Pawns poison attackers on death.", "p": "poison", "n": "stealth", "b": "medic", "r": "juggernaut", "q": "assassin", "k": "shield"},
    5:  {"name": "5. Arcane Coven", "desc": "Bishops teleport to empty squares; Queen swaps with allies.", "p": "hive", "n": "trample", "b": "blink", "r": "broadside", "q": "swap", "k": "chaos"},
    6:  {"name": "6. Mongol Raiders", "desc": "Knights get bonus moves on capture; Bishops shoot 2 squares ahead.", "p": "berserk", "n": "hit_and_run", "b": "archer", "r": "juggernaut", "q": "dragon_breath", "k": "shield"},
    7:  {"name": "7. Goblin Swarm", "desc": "Pawns explode on death, killing adjacent enemies.", "p": "bomber", "n": "duelist", "b": "revive", "r": "broadside", "q": "broodmother", "k": "aura_kill"},
    8:  {"name": "8. Dwarven Ironclad", "desc": "All pieces are immune to Pawn captures; Rooks crush obstacles.", "p": "armored", "n": "armored", "b": "armored", "r": "juggernaut", "q": "armored", "k": "titan"},
    9:  {"name": "9. Roman Legion", "desc": "Adjacent pawns boost each other; Bishops heal lost pawns.", "p": "legion", "n": "double_jump", "b": "medic", "r": "stun", "q": "shield", "k": "freeze"},
    10: {"name": "10. Vampire Aristocracy", "desc": "Captures convert enemy pieces into White pieces; Queen drains neighbors.", "p": "poison", "n": "vampire", "b": "vampire", "r": "freeze", "q": "aura_kill", "k": "shield"},
    11: {"name": "11. Samurai Clan", "desc": "Knights duel adjacent pieces; Queen strikes all orthogonal neighbors.", "p": "pike", "n": "duelist", "b": "cavalry", "r": "broadside", "q": "cleave", "k": "titan"},
    12: {"name": "12. Viking Berserkers", "desc": "Pieces gain consecutive turns on kill.", "p": "berserk", "n": "berserk", "b": "freeze", "r": "juggernaut", "q": "berserk", "k": "shield"},
    13: {"name": "13. Steampunk Automata", "desc": "Rooks fire lasers down files without moving; Pawns self-destruct.", "p": "bomber", "n": "stealth", "b": "sniper", "r": "laser", "q": "aura_kill", "k": "plague"},
    14: {"name": "14. Eldritch Cult", "desc": "Bishops mind-control adjacent enemy pawns; Queen induces madness.", "p": "plague", "n": "chaos", "b": "convert", "r": "freeze", "q": "chaos", "k": "shield"},
    15: {"name": "15. Elven Rangers", "desc": "Bishops and Queen snipe enemies from range without moving.", "p": "archer", "n": "double_jump", "b": "sniper", "r": "broadside", "q": "sniper", "k": "titan"},
    16: {"name": "16. Frost Giants", "desc": "Rooks freeze adjacent enemies.", "p": "freeze", "n": "trample", "b": "freeze", "r": "freeze", "q": "freeze", "k": "freeze"},
    17: {"name": "17. Fire Elementals", "desc": "Queen incinerates all adjacent enemy pieces on arrival.", "p": "plague", "n": "duelist", "b": "blink", "r": "aura_kill", "q": "aura_kill", "k": "titan"},
    18: {"name": "18. Shadow Stalkers", "desc": "Pawns move diagonally; Knights jump twice.", "p": "shadow_pawn", "n": "double_jump", "b": "cavalry", "r": "freeze", "q": "chaos", "k": "shield"},
    19: {"name": "19. Celestial Host", "desc": "Bishops resurrect captured allies; Queen shields neighbors.", "p": "hive", "n": "shield", "b": "revive", "r": "stun", "q": "shield", "k": "revive"},
    20: {"name": "20. Abyssal Demons", "desc": "Queen teleports and strikes adjacent foes.", "p": "plague", "n": "trample", "b": "blink", "r": "juggernaut", "q": "demon_blink", "k": "titan"},
    21: {"name": "21. Ninja Syndicate", "desc": "Pawns poison attackers; Knights trample enemies.", "p": "poison", "n": "trample", "b": "archer", "r": "freeze", "q": "assassin", "k": "shield"},
    22: {"name": "22. Clockwork Golems", "desc": "Pieces cannot be captured by Queens or Rooks.", "p": "heavy_armor", "n": "heavy_armor", "b": "heavy_armor", "r": "heavy_armor", "q": "heavy_armor", "k": "titan"},
    23: {"name": "23. Pirate Armada", "desc": "Rooks fire broadsides (kill left/right).", "p": "hive", "n": "duelist", "b": "sniper", "r": "broadside", "q": "broadside", "k": "broadside"},
    24: {"name": "24. Hive Mind", "desc": "Queen spawns extra pawns on adjacent empty squares.", "p": "hive", "n": "trample", "b": "blink", "r": "juggernaut", "q": "broodmother", "k": "shield"},
    25: {"name": "25. Chronomancers", "desc": "Bishops slow enemies; Queen rewinds threats.", "p": "plague", "n": "double_jump", "b": "freeze", "r": "stun", "q": "chrono", "k": "titan"},
    26: {"name": "26. Dragonkin", "desc": "Queen breathes fire in a 3-square line.", "p": "bomber", "n": "trample", "b": "archer", "r": "juggernaut", "q": "dragon_breath", "k": "shield"},
    27: {"name": "27. Plague Bringers", "desc": "ALL White pieces infect adjacent Black pieces (die in 3 turns).", "p": "plague", "n": "plague", "b": "plague", "r": "plague", "q": "plague", "k": "plague"},
    28: {"name": "28. Royal Guard", "desc": "Knights protect adjacent allies from capture.", "p": "armored", "n": "shield", "b": "blink", "r": "freeze", "q": "shield", "k": "titan"},
    29: {"name": "29. Chaos Jester", "desc": "Pieces trigger random special effects on move.", "p": "chaos", "n": "chaos", "b": "chaos", "r": "chaos", "q": "chaos", "k": "chaos"},
    30: {"name": "30. Godslayer Titan", "desc": "Queen is invincible and destroys everything in a 1-square radius.", "p": "titan", "n": "berserk", "b": "blink", "r": "juggernaut", "q": "titan", "k": "titan"}
}

POWER_DESCRIPTIONS = {
    "pike": "Kills a non-king enemy sandwiched between this unit and a White pawn.",
    "templar": "A defending unit destroys an attacking pawn, knight, or bishop.",
    "cavalry": "Tramples adjacent enemies after moving.",
    "catapult": "Shoots aligned enemies up to four squares away through a clear line.",
    "plague": "Infects adjacent enemies; they die after three full turns.",
    "undead": "A captured White pawn respawns on rank two.",
    "necromancer": "A captured enemy piece is raised as a White piece.",
    "phalanx": "White pawns cannot be captured from the front.",
    "stun": "Stuns adjacent enemies for their next turn.",
    "poison": "A piece that captures this defender is destroyed instead.",
    "stealth": "This unit is rendered as a ghost.",
    "assassin": "Destroys adjacent enemies after moving.",
    "blink": "Teleports to any empty square.",
    "swap": "The Queen can swap places with a White ally.",
    "hit_and_run": "Capturing grants White another move.",
    "archer": "Shoots an aligned enemy exactly two squares away.",
    "bomber": "Goblin pawns explode when captured; Steampunk pawns self-destruct after moving.",
    "armored": "Immune to captures by enemy pawns.",
    "juggernaut": "Rooks can crush enemy blockers and destroy adjacent enemies.",
    "legion": "Adjacent White pawns strengthen one another.",
    "medic": "A bishop can restore a captured White pawn when it moves.",
    "vampire": "A captured enemy piece is raised as a White piece.",
    "aura_kill": "Destroys adjacent enemies after moving.",
    "duelist": "Destroys adjacent enemies after moving.",
    "cleave": "Destroys enemies on the four orthogonal neighboring squares.",
    "berserk": "Capturing grants White another move.",
    "laser": "Shoots enemies on the same file through a clear line.",
    "convert": "Converts adjacent enemy pawns to White after moving.",
    "chaos": "Each move triggers a random blast, pawn spawn, or short shift.",
    "sniper": "Shoots any aligned enemy through a clear line.",
    "freeze": "Freezes adjacent enemies for their next turn.",
    "shadow_pawn": "May move one square diagonally into an empty square.",
    "double_jump": "Knights can make two jumps in one turn.",
    "revive": "A bishop can revive a captured White ally when it moves.",
    "shield": "Protects adjacent White allies from capture.",
    "demon_blink": "The Queen teleports to an empty square and destroys adjacent enemies.",
    "trample": "Destroys adjacent enemies after moving.",
    "heavy_armor": "Immune to captures by enemy rooks and queens.",
    "broadside": "After moving, destroys the first enemy on its rank in each direction.",
    "hive": "A move spawns a pawn on the first adjacent empty square.",
    "broodmother": "A move spawns pawns on every adjacent empty square.",
    "chrono": "Freezes enemies next to the White Queen for their next turn.",
    "dragon_breath": "Destroys enemies in the next three squares on the same file.",
    "titan": "Cannot be captured; destroys adjacent enemies after moving.",
}

for army_id, army in ARMIES.items():
    for slot in ("p", "n", "b", "r", "q", "k"):
        if army.get(slot) not in POWER_DESCRIPTIONS:
            raise ValueError(f"Army {army_id} has no implemented power for slot {slot!r}.")

POWER_SLOT_ORDER = ("p", "n", "b", "r", "q", "k")
UNIQUE_POWER_VECTORS = {}
move_vectors = [
    (df, dr)
    for distance in range(1, 8)
    for df in range(-distance, distance + 1)
    for dr in range(-distance, distance + 1)
    if max(abs(df), abs(dr)) == distance
]
if len(move_vectors) < len(ARMIES) * len(POWER_SLOT_ORDER):
    raise ValueError("Not enough unique move vectors for every army piece.")

for army_id, army in ARMIES.items():
    army["desc"] = "Every piece has its own globally unique special move."
    for slot in POWER_SLOT_ORDER:
        power_id = f"unique_{army_id}_{slot}"
        vector = move_vectors[len(UNIQUE_POWER_VECTORS)]
        UNIQUE_POWER_VECTORS[power_id] = vector
        army[slot] = power_id
        POWER_DESCRIPTIONS[power_id] = (
            f"May jump by Δfile {vector[0]:+d}, Δrank {vector[1]:+d}, "
            "over intervening pieces; captures non-king enemies."
        )

class AsymmetricBoard:
    def __init__(self, army_config, roster_counts=None):
        self.board = chess.Board()
        self.army = army_config
        self.plague_timers = {}
        self.stun_timers = {}
        self.captured_white = []
        self.event_log = []
        self.position_history = []
        self.position_counts = {}
        if roster_counts:
            self._apply_custom_roster(roster_counts)
        self._record_position()

    def _apply_custom_roster(self, counts):
        self.board.castling_rights &= ~chess.BB_RANK_1
        for sq in chess.SQUARES:
            p = self.board.piece_at(sq)
            if p and p.color == chess.WHITE and p.piece_type != chess.KING:
                self.board.remove_piece_at(sq)

        pawn_slots = [chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2]
        for sq in pawn_slots[:counts.get(chess.PAWN, 0)]:
            self.board.set_piece_at(sq, chess.Piece(chess.PAWN, chess.WHITE))

        preferred_slots = {
            chess.KNIGHT: [chess.B1, chess.G1],
            chess.BISHOP: [chess.C1, chess.F1],
            chess.ROOK: [chess.A1, chess.H1],
            chess.QUEEN: [chess.D1],
        }
        overflow_counts = {}
        for piece_type, slots in preferred_slots.items():
            count = counts.get(piece_type, 0)
            for square in slots[:count]:
                self.board.set_piece_at(square, chess.Piece(piece_type, chess.WHITE))
            overflow_counts[piece_type] = max(0, count - len(slots))

        overflow_slots = [chess.A1, chess.B1, chess.C1, chess.D1, chess.F1, chess.G1, chess.H1]
        for piece_type, overflow_count in overflow_counts.items():
            for _ in range(overflow_count):
                square = next((sq for sq in overflow_slots if not self.board.piece_at(sq)), None)
                if square is None:
                    return
                self.board.set_piece_at(square, chess.Piece(piece_type, chess.WHITE))

    def _record_position(self):
        position_key = self._position_key()
        self.position_counts[position_key] = self.position_counts.get(position_key, 0) + 1
        self.position_history.append({
            "board": self.board.copy(stack=False),
            "plague_timers": self.plague_timers.copy(),
            "stun_timers": self.stun_timers.copy(),
            "captured_white": self.captured_white.copy(),
            "event_log": self.event_log.copy(),
            "position_key": position_key,
        })

    def _position_key(self):
        return (
            self.board.board_fen(),
            self.board.turn,
            self.board.castling_rights,
            self.board.ep_square if self.board.has_legal_en_passant() else None,
            tuple(sorted(self.plague_timers.items())),
            tuple(sorted(self.stun_timers.items())),
        )

    def game_over_reason(self):
        if self.board.king(self.board.turn) is None:
            return "checkmate"
        if not self.get_custom_legal_moves():
            return "checkmate" if self.board.is_check() else "stalemate"
        if self.position_counts.get(self._position_key(), 0) >= 3:
            return "repetition"
        return None

    def is_game_over(self):
        return self.game_over_reason() is not None

    def result(self):
        reason = self.game_over_reason()
        if reason == "checkmate":
            return "0-1" if self.board.turn == chess.WHITE else "1-0"
        return "1/2-1/2" if reason else "*"

    def copy(self):
        new_b = AsymmetricBoard(self.army)
        new_b.board = self.board.copy()
        new_b.plague_timers = self.plague_timers.copy()
        new_b.stun_timers = self.stun_timers.copy()
        new_b.captured_white = self.captured_white.copy()
        new_b.event_log = self.event_log.copy()
        new_b.position_history = []
        new_b.position_counts = self.position_counts.copy()
        return new_b

    def get_ability(self, piece_type):
        mapping = {
            chess.PAWN: self.army["p"],
            chess.KNIGHT: self.army["n"],
            chess.BISHOP: self.army["b"],
            chess.ROOK: self.army["r"],
            chess.QUEEN: self.army["q"],
            chess.KING: self.army["k"]
        }
        return mapping[piece_type]

    def _is_protected(self, square):
        for neighbor in self._get_neighbors(square):
            piece = self.board.piece_at(neighbor)
            if piece and piece.color == chess.WHITE and self.get_ability(piece.piece_type) == "shield":
                return True
        return False

    def _black_capture_is_blocked(self, move):
        attacker = self.board.piece_at(move.from_square)
        defender = self.board.piece_at(move.to_square)
        if not attacker or attacker.color != chess.BLACK or not defender or defender.color != chess.WHITE:
            return False

        ability = self.get_ability(defender.piece_type)
        if ability == "armored" and attacker.piece_type == chess.PAWN:
            return True
        if ability == "heavy_armor" and attacker.piece_type in (chess.ROOK, chess.QUEEN):
            return True
        if ability == "phalanx" and defender.piece_type == chess.PAWN:
            if chess.square_rank(move.from_square) > chess.square_rank(move.to_square):
                return True
        return self._is_protected(move.to_square)

    def _line_is_clear(self, start, end):
        start_file, start_rank = chess.square_file(start), chess.square_rank(start)
        end_file, end_rank = chess.square_file(end), chess.square_rank(end)
        df, dr = end_file - start_file, end_rank - start_rank
        if not (df == 0 or dr == 0 or abs(df) == abs(dr)):
            return False

        file_step = (df > 0) - (df < 0)
        rank_step = (dr > 0) - (dr < 0)
        distance = max(abs(df), abs(dr))
        for step in range(1, distance):
            square = chess.square(start_file + file_step * step, start_rank + rank_step * step)
            if self.board.piece_at(square):
                return False
        return True

    def get_custom_legal_moves(self):
        moves = [move for move in self.board.legal_moves if not self._black_capture_is_blocked(move)]
        if self.board.turn != chess.WHITE:
            return [move for move in moves if move.from_square not in self.stun_timers]

        for sq, piece in self.board.piece_map().items():
            if piece.color != chess.WHITE:
                continue
            ability = self.get_ability(piece.piece_type)

            if ability in UNIQUE_POWER_VECTORS:
                df, dr = UNIQUE_POWER_VECTORS[ability]
                target_file = chess.square_file(sq) + df
                target_rank = chess.square_rank(sq) + dr
                if 0 <= target_file <= 7 and 0 <= target_rank <= 7:
                    target_sq = chess.square(target_file, target_rank)
                    target_piece = self.board.piece_at(target_sq)
                    if not target_piece or (
                        target_piece.color == chess.BLACK
                        and target_piece.piece_type != chess.KING
                    ):
                        promotion = (
                            chess.QUEEN
                            if piece.piece_type == chess.PAWN and target_rank == 7
                            else None
                        )
                        special_move = chess.Move(sq, target_sq, promotion=promotion)
                        if special_move not in self.board.legal_moves:
                            simulated = self.board.copy(stack=False)
                            simulated.push(special_move)
                            king_square = simulated.king(chess.WHITE)
                            if king_square is not None and not simulated.is_attacked_by(
                                chess.BLACK, king_square
                            ):
                                moves.append(special_move)

            if ability in ["sniper", "laser", "catapult", "archer"]:
                for target_sq, target_p in self.board.piece_map().items():
                    if target_p.color == chess.BLACK and target_p.piece_type != chess.KING:
                        distance = max(
                            abs(chess.square_file(sq) - chess.square_file(target_sq)),
                            abs(chess.square_rank(sq) - chess.square_rank(target_sq))
                        )
                        aligned = self._line_is_clear(sq, target_sq)
                        same_file = chess.square_file(sq) == chess.square_file(target_sq)
                        if aligned and (
                            (ability == "archer" and distance == 2) or
                            (ability == "catapult" and distance <= 4) or
                            (ability == "sniper") or
                            (ability == "laser" and same_file)
                        ):
                            moves.append(("RANGED_KILL", sq, target_sq))

            if ability == "blink" or (ability == "demon_blink" and piece.piece_type == chess.QUEEN):
                for target_sq in chess.SQUARES:
                    if not self.board.piece_at(target_sq):
                        moves.append(("TELEPORT", sq, target_sq))

            if ability == "shadow_pawn" and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(sq) + 1
                file = chess.square_file(sq)
                if rank <= 7:
                    for target_file in (file - 1, file + 1):
                        if 0 <= target_file <= 7:
                            target_sq = chess.square(target_file, rank)
                            if not self.board.piece_at(target_sq):
                                moves.append(("SHADOW_MOVE", sq, target_sq))

            if ability == "swap" and piece.piece_type == chess.QUEEN:
                for target_sq, target_piece in self.board.piece_map().items():
                    if target_piece.color == chess.WHITE and target_sq != sq:
                        moves.append(("SWAP", sq, target_sq))

            if ability == "double_jump" and piece.piece_type == chess.KNIGHT:
                first_offsets = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
                file, rank = chess.square_file(sq), chess.square_rank(sq)
                for df1, dr1 in first_offsets:
                    middle_file, middle_rank = file + df1, rank + dr1
                    if not (0 <= middle_file <= 7 and 0 <= middle_rank <= 7):
                        continue
                    middle_sq = chess.square(middle_file, middle_rank)
                    if self.board.piece_at(middle_sq):
                        continue
                    for df2, dr2 in first_offsets:
                        target_file, target_rank = middle_file + df2, middle_rank + dr2
                        if not (0 <= target_file <= 7 and 0 <= target_rank <= 7):
                            continue
                        target_sq = chess.square(target_file, target_rank)
                        target_piece = self.board.piece_at(target_sq)
                        if target_sq != sq and (not target_piece or (target_piece.color == chess.BLACK and target_piece.piece_type != chess.KING)):
                            moves.append(("DOUBLE_JUMP", sq, target_sq))

            if ability == "juggernaut" and piece.piece_type == chess.ROOK:
                for df, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    file, rank = chess.square_file(sq), chess.square_rank(sq)
                    crushed = False
                    while True:
                        file += df
                        rank += dr
                        if not (0 <= file <= 7 and 0 <= rank <= 7):
                            break
                        target_sq = chess.square(file, rank)
                        target_piece = self.board.piece_at(target_sq)
                        if target_piece:
                            if target_piece.color == chess.WHITE or target_piece.piece_type == chess.KING:
                                break
                            crushed = True
                            continue
                        if crushed:
                            moves.append(("CRUSH", sq, target_sq))
        return moves

    def push_custom_move(self, move, log_events=False):
        if isinstance(move, tuple) and move[0] == "RANGED_KILL":
            _, attacker_sq, target_sq = move
            victim = self.board.piece_at(target_sq)
            if not victim or victim.piece_type == chess.KING:
                return
            self.board.remove_piece_at(target_sq)
            if log_events and victim:
                self.event_log.append(f"💥 Ranged strike from {chess.square_name(attacker_sq)} destroyed {victim.symbol().upper()} on {chess.square_name(target_sq)}!")
            self.board.turn = chess.BLACK
            self._tick_end_of_turn(log_events)
            self._record_position()
            return

        if isinstance(move, tuple) and move[0] == "SWAP":
            _, attacker_sq, target_sq = move
            attacker = self.board.piece_at(attacker_sq)
            ally = self.board.piece_at(target_sq)
            if attacker and ally:
                self.board.remove_piece_at(attacker_sq)
                self.board.remove_piece_at(target_sq)
                self.board.set_piece_at(target_sq, attacker)
                self.board.set_piece_at(attacker_sq, ally)
                self.board.turn = chess.BLACK
                if log_events:
                    self.event_log.append(f"🔀 The Queen swapped places with an ally on {chess.square_name(target_sq)}!")
                self._tick_end_of_turn(log_events)
                self._record_position()
            return

        if isinstance(move, tuple):
            action, attacker_sq, target_sq = move
            if action == "CRUSH":
                start_file, start_rank = chess.square_file(attacker_sq), chess.square_rank(attacker_sq)
                end_file, end_rank = chess.square_file(target_sq), chess.square_rank(target_sq)
                file_step = (end_file > start_file) - (end_file < start_file)
                rank_step = (end_rank > start_rank) - (end_rank < start_rank)
                file, rank = start_file + file_step, start_rank + rank_step
                while (file, rank) != (end_file, end_rank):
                    blocker_sq = chess.square(file, rank)
                    blocker = self.board.piece_at(blocker_sq)
                    if blocker and blocker.color == chess.BLACK and blocker.piece_type != chess.KING:
                        self.board.remove_piece_at(blocker_sq)
                        if log_events:
                            self.event_log.append(f"⚙️ Juggernaut crushed an obstacle on {chess.square_name(blocker_sq)}!")
                    file += file_step
                    rank += rank_step
            move = chess.Move(attacker_sq, target_sq)

        attacker = self.board.piece_at(move.from_square)
        defender = self.board.piece_at(move.to_square)
        if defender and defender.piece_type == chess.KING:
            return
        is_white = (self.board.turn == chess.WHITE)
        used_unique_move = False
        if is_white and attacker:
            ability = self.get_ability(attacker.piece_type)
            if ability in UNIQUE_POWER_VECTORS:
                df, dr = UNIQUE_POWER_VECTORS[ability]
                used_unique_move = (
                    chess.square_file(move.to_square) - chess.square_file(move.from_square) == df
                    and chess.square_rank(move.to_square) - chess.square_rank(move.from_square) == dr
                    and move not in self.board.legal_moves
                )

        if not is_white and defender and defender.color == chess.WHITE:
            def_ability = self.get_ability(defender.piece_type)
            if def_ability == "templar" and attacker.piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP]:
                self.board.remove_piece_at(move.from_square)
                if log_events:
                    self.event_log.append(f"🛡️ Templar armor shattered Stockfish's {attacker.symbol().upper()}!")
                self.board.turn = chess.WHITE
                self._tick_end_of_turn(log_events)
                self._record_position()
                return
            if def_ability == "titan":
                self.board.remove_piece_at(move.from_square)
                if log_events:
                    self.event_log.append(f"⚡ Godslayer Titan annihilated attacker {attacker.symbol().upper()}!")
                self.board.turn = chess.WHITE
                self._tick_end_of_turn(log_events)
                self._record_position()
                return
            if def_ability == "poison":
                self.board.remove_piece_at(move.from_square)
                if log_events:
                    self.event_log.append(f"☠️ Poisoned pawn killed Stockfish's {attacker.symbol().upper()}!")
                self.board.turn = chess.WHITE
                self._tick_end_of_turn(log_events)
                self._record_position()
                return
            if self._black_capture_is_blocked(move):
                self.board.turn = chess.WHITE
                self._tick_end_of_turn(log_events)
                self._record_position()
                return

        if not is_white and defender and defender.color == chess.WHITE:
            self.captured_white.append(defender)
        if not is_white and move.from_square in self.plague_timers:
            self.plague_timers[move.to_square] = self.plague_timers.pop(move.from_square)
        self.board.push(move)

        if is_white and attacker:
            ability = self.get_ability(attacker.piece_type)
            dest = move.to_square
            if log_events and used_unique_move:
                df, dr = UNIQUE_POWER_VECTORS[ability]
                self.event_log.append(
                    f"✨ {chess.piece_name(attacker.piece_type).title()} used its unique move "
                    f"({df:+d} files, {dr:+d} ranks)!"
                )
            self._resolve_white_ability(ability, move.from_square, dest, defender, log_events)
        elif not is_white and defender and defender.color == chess.WHITE:
            if defender.piece_type == chess.PAWN:
                ability = self.get_ability(chess.PAWN)
                if ability == "undead":
                    self._spawn_piece(chess.PAWN, chess.WHITE, chess.BB_RANK_2, log_events)
                    if self.captured_white and self.captured_white[-1].piece_type == chess.PAWN:
                        self.captured_white.pop()
                if ability == "bomber":
                    for square in [move.to_square] + self._get_neighbors(move.to_square):
                        piece = self.board.piece_at(square)
                        if piece and piece.color == chess.BLACK and piece.piece_type != chess.KING:
                            self.board.remove_piece_at(square)
                    if log_events:
                        self.event_log.append(f"💣 Goblin pawn exploded on {chess.square_name(move.to_square)}!")
        self._tick_end_of_turn(log_events)
        self._record_position()

    def _resolve_white_ability(self, ability, start, dest, captured, log_events):
        if ability == "pike":
            self._resolve_pikeman_sandwich(dest, log_events)
        elif ability == "cavalry":
            self._resolve_cavalry_trample(start, dest, log_events)

        if ability == "plague":
            for square in self._get_neighbors(dest):
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.BLACK and piece.piece_type != chess.KING:
                    self.plague_timers[square] = 6
                    if log_events:
                        self.event_log.append(f"🦠 {piece.symbol().upper()} on {chess.square_name(square)} caught the plague!")

        if ability in ("aura_kill", "titan", "assassin", "duelist", "cleave", "trample", "juggernaut", "demon_blink", "cavalry"):
            orthogonal_only = ability == "cleave"
            for square in self._get_neighbors(dest):
                if orthogonal_only and (
                    chess.square_file(square) != chess.square_file(dest)
                    and chess.square_rank(square) != chess.square_rank(dest)
                ):
                    continue
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.BLACK and piece.piece_type != chess.KING:
                    self.board.remove_piece_at(square)
                    if log_events:
                        self.event_log.append(f"⚔️ {ability.replace('_', ' ').title()} struck {piece.symbol().upper()} on {chess.square_name(square)}!")

        if ability == "broadside":
            file, rank = chess.square_file(dest), chess.square_rank(dest)
            for direction in (-1, 1):
                target_file = file + direction
                while 0 <= target_file <= 7:
                    square = chess.square(target_file, rank)
                    piece = self.board.piece_at(square)
                    if piece:
                        if piece.color == chess.BLACK and piece.piece_type != chess.KING:
                            self.board.remove_piece_at(square)
                            if log_events:
                                self.event_log.append(f"🏴‍☠️ Broadside struck {piece.symbol().upper()} on {chess.square_name(square)}!")
                        break
                    target_file += direction

        if ability == "bomber" and "Steampunk Automata" in self.army["name"]:
            for square in [dest] + self._get_neighbors(dest):
                piece = self.board.piece_at(square)
                if piece and square == dest and piece.color == chess.WHITE and piece.piece_type == chess.PAWN:
                    self.board.remove_piece_at(square)
                elif piece and piece.color == chess.BLACK and piece.piece_type != chess.KING:
                    self.board.remove_piece_at(square)
            if log_events:
                self.event_log.append(f"💣 Steampunk pawn self-destructed on {chess.square_name(dest)}!")

        if ability == "convert":
            for square in self._get_neighbors(dest):
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.BLACK and piece.piece_type == chess.PAWN:
                    self.board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))
                    self.plague_timers.pop(square, None)
                    if log_events:
                        self.event_log.append(f"🔮 Mind-controlled pawn on {chess.square_name(square)}!")

        if captured and ability in ("vampire", "necromancer"):
            self._spawn_piece(captured.piece_type, chess.WHITE, self._neighbor_mask(dest), log_events)

        if ability == "freeze" or ability == "stun":
            for square in self._get_neighbors(dest):
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.BLACK:
                    self.stun_timers[square] = 2
                    if log_events:
                        self.event_log.append(f"❄️ {piece.symbol().upper()} on {chess.square_name(square)} is stunned!")

        if ability in ("hive", "broodmother"):
            spawn_squares = self._get_neighbors(dest)
            if ability == "hive":
                spawn_squares = [square for square in spawn_squares if not self.board.piece_at(square)][:1]
            for square in spawn_squares:
                if not self.board.piece_at(square):
                    self.board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))
                    if log_events:
                        self.event_log.append(f"🐝 A new pawn emerged on {chess.square_name(square)}!")

        if ability == "medic":
            pawn_index = next((index for index, piece in enumerate(self.captured_white)
                               if piece.piece_type == chess.PAWN), None)
            if pawn_index is not None:
                self.captured_white.pop(pawn_index)
                self._spawn_piece(chess.PAWN, chess.WHITE, chess.BB_RANK_2, log_events)
        elif ability == "revive" and self.captured_white:
            piece = self.captured_white.pop()
            self._spawn_piece(piece.piece_type, chess.WHITE, chess.BB_RANK_2 | chess.BB_RANK_1, log_events)

        if ability == "dragon_breath":
            file, rank = chess.square_file(dest), chess.square_rank(dest)
            for distance in range(1, 4):
                target_rank = rank + distance
                if target_rank > 7:
                    break
                square = chess.square(file, target_rank)
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.BLACK and piece.piece_type != chess.KING:
                    self.board.remove_piece_at(square)
                    if log_events:
                        self.event_log.append(f"🔥 Dragon breath consumed a piece on {chess.square_name(square)}!")

        if ability == "chrono":
            queen_squares = [square for square, piece in self.board.piece_map().items()
                             if piece.color == chess.WHITE and piece.piece_type == chess.QUEEN]
            for queen_sq in queen_squares:
                for square in self._get_neighbors(queen_sq):
                    piece = self.board.piece_at(square)
                    if piece and piece.color == chess.BLACK:
                        self.stun_timers[square] = 2
            if log_events:
                self.event_log.append("⏳ Chronomancer rewound nearby threats for one turn!")

        if ability == "chaos":
            effect = random.choice(("blast", "spawn", "shift"))
            enemies = [square for square in self._get_neighbors(dest)
                       if (piece := self.board.piece_at(square)) and piece.color == chess.BLACK and piece.piece_type != chess.KING]
            empty = [square for square in self._get_neighbors(dest) if not self.board.piece_at(square)]
            if effect == "blast" and enemies:
                target = random.choice(enemies)
                self.board.remove_piece_at(target)
            elif effect == "spawn" and empty:
                self.board.set_piece_at(random.choice(empty), chess.Piece(chess.PAWN, chess.WHITE))
            elif effect == "shift" and empty:
                target = random.choice(empty)
                moved = self.board.remove_piece_at(dest)
                if moved:
                    self.board.set_piece_at(target, moved)
            if log_events:
                self.event_log.append("🃏 Chaos triggered a random battlefield effect!")

        if captured and ability in ("hit_and_run", "berserk"):
            self.board.turn = chess.WHITE
            if log_events:
                self.event_log.append("⚡ The attacker earned an extra turn!")

    def _neighbor_mask(self, square):
        mask = 0
        for neighbor in self._get_neighbors(square):
            mask |= chess.BB_SQUARES[neighbor]
        return mask

    def _spawn_piece(self, piece_type, color, mask, log_events=False):
        for square in chess.scan_forward(mask):
            if not self.board.piece_at(square):
                self.board.set_piece_at(square, chess.Piece(piece_type, color))
                if log_events:
                    self.event_log.append(f"✨ {chess.piece_name(piece_type).title()} revived on {chess.square_name(square)}!")
                return True
        for square in chess.SQUARES:
            if not self.board.piece_at(square):
                self.board.set_piece_at(square, chess.Piece(piece_type, color))
                if log_events:
                    self.event_log.append(f"✨ {chess.piece_name(piece_type).title()} revived on {chess.square_name(square)}!")
                return True
        return False
    def _resolve_pikeman_sandwich(self, sq, log_events):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        f, r = chess.square_file(sq), chess.square_rank(sq)
        for df, dr in directions:
            mid_f, mid_r = f + df, r + dr
            far_f, far_r = f + 2*df, r + 2*dr
            if 0 <= far_f <= 7 and 0 <= far_r <= 7:
                mid_sq = chess.square(mid_f, mid_r)
                far_sq = chess.square(far_f, far_r)
                mid_p = self.board.piece_at(mid_sq)
                far_p = self.board.piece_at(far_sq)
                if mid_p and mid_p.color == chess.BLACK and mid_p.piece_type != chess.KING:
                    if far_p and far_p.color == chess.WHITE and far_p.piece_type == chess.PAWN:
                        self.board.remove_piece_at(mid_sq)
                        if log_events:
                            self.event_log.append(f"🔱 Pikemen sandwiched and killed {mid_p.symbol().upper()} on {chess.square_name(mid_sq)}!")

    def _resolve_cavalry_trample(self, start, end, log_events):
        f1, r1 = chess.square_file(start), chess.square_rank(start)
        f2, r2 = chess.square_file(end), chess.square_rank(end)
        if abs(f2 - f1) != abs(r2 - r1):
            return
        df = (f2 > f1) - (f2 < f1)
        dr = (r2 > r1) - (r2 < r1)
        distance = abs(f2 - f1)
        for step in range(1, distance):
            curr_f, curr_r = f1 + df * step, r1 + dr * step
            sq = chess.square(curr_f, curr_r)
            p = self.board.piece_at(sq)
            if p and p.color == chess.BLACK and p.piece_type != chess.KING:
                self.board.remove_piece_at(sq)
                if log_events:
                    self.event_log.append(f"🐎 Cavalry trampled {p.symbol().upper()} on {chess.square_name(sq)}!")

    def _get_neighbors(self, sq):
        neighbors = []
        f, r = chess.square_file(sq), chess.square_rank(sq)
        for df in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if df == 0 and dr == 0:
                    continue
                if 0 <= f + df <= 7 and 0 <= r + dr <= 7:
                    neighbors.append(chess.square(f + df, r + dr))
        return neighbors

    def _tick_end_of_turn(self, log_events=False):
        expired = []
        for sq, timer in list(self.plague_timers.items()):
            p = self.board.piece_at(sq)
            if not p or p.color == chess.WHITE:
                expired.append(sq)
                continue
            self.plague_timers[sq] -= 1
            if self.plague_timers[sq] <= 0:
                self.board.remove_piece_at(sq)
                expired.append(sq)
                if log_events:
                    self.event_log.append(f"💀 {p.symbol().upper()} on {chess.square_name(sq)} died of the plague!")
                for adj in self._get_neighbors(sq):
                    adj_p = self.board.piece_at(adj)
                    if adj_p and adj_p.color == chess.BLACK and adj_p.piece_type != chess.KING:
                        self.plague_timers[adj] = 6
        for sq in expired:
            self.plague_timers.pop(sq, None)

        for square, timer in list(self.stun_timers.items()):
            piece = self.board.piece_at(square)
            if not piece or piece.color != chess.BLACK or timer <= 1:
                self.stun_timers.pop(square, None)
            else:
                self.stun_timers[square] = timer - 1
PIECE_VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}

def evaluate_board(custom_board):
    if custom_board.game_over_reason() == "checkmate":
        return -99999 if custom_board.board.turn == chess.WHITE else 99999
    if custom_board.is_game_over():
        return 0
    score = 0
    for sq, piece in custom_board.board.piece_map().items():
        val = PIECE_VALUES[piece.piece_type]
        if piece.color == chess.WHITE:
            score += val
            if piece.piece_type == chess.PAWN:
                adjacent = [neighbor for neighbor in custom_board._get_neighbors(sq)
                            if (neighbor_piece := custom_board.board.piece_at(neighbor))
                            and neighbor_piece.color == chess.WHITE
                            and neighbor_piece.piece_type == chess.PAWN]
                if adjacent and custom_board.get_ability(chess.PAWN) == "legion":
                    score += 25
        else:
            score -= val
            if sq in custom_board.plague_timers:
                score += 180
    return score

def get_best_custom_move(custom_board, depth=2, for_white=True):
    best_move = None
    best_eval = -float('inf') if for_white else float('inf')
    moves = custom_board.get_custom_legal_moves()
    if not moves:
        return None, evaluate_board(custom_board)
    random.shuffle(moves)
    alpha, beta = -float('inf'), float('inf')

    for move in moves:
        sim = custom_board.copy()
        sim.push_custom_move(move)
        ev = minimax(sim, depth - 1, alpha, beta, not for_white)
        if for_white and ev > best_eval:
            best_eval = ev
            best_move = move
            alpha = max(alpha, best_eval)
        elif not for_white and ev < best_eval:
            best_eval = ev
            best_move = move
            beta = min(beta, best_eval)
    return best_move, best_eval

def minimax(custom_board, depth, alpha, beta, maximizing):
    if depth == 0 or custom_board.is_game_over():
        return evaluate_board(custom_board)
    moves = custom_board.get_custom_legal_moves()
    if not moves:
        return evaluate_board(custom_board)
    if maximizing:
        max_eval = -float('inf')
        for move in moves:
            sim = custom_board.copy()
            sim.push_custom_move(move)
            ev = minimax(sim, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, ev)
            alpha = max(alpha, ev)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            sim = custom_board.copy()
            sim.push_custom_move(move)
            ev = minimax(sim, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, ev)
            beta = min(beta, ev)
            if beta <= alpha:
                break
        return min_eval


PIECE_ART = {
    chess.PAWN: (
        '<circle cx="50" cy="27" r="11" fill="{piece_fill}" stroke="{ink}" stroke-width="5"/>'
        '<path d="M37 43 L63 43 L70 70 L79 80 L21 80 L30 70 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M28 84 H72" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>'
    ),
    chess.KNIGHT: (
        '<path d="M24 80 L27 67 L22 55 L31 42 L36 26 L49 35 L61 32 L75 45 L71 56 L78 66 L76 80 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M37 28 L39 17 L51 25 L61 24 L67 34 L50 38 Z" fill="{accent}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
        '<circle cx="57" cy="45" r="3.5" fill="{ink}"/>'
    ),
    chess.BISHOP: (
        '<path d="M50 18 L67 38 L63 54 L73 70 L81 80 L19 80 L27 70 L37 54 L33 38 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M39 37 L61 57" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M27 84 H73" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    ),
    chess.ROOK: (
        '<path d="M26 22 H39 V34 H47 V22 H60 V34 H68 V22 H78 V45 L72 52 V75 L82 82 H18 L28 75 V52 L22 45 V22 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M35 55 H65 M36 65 H64" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>'
    ),
    chess.QUEEN: (
        '<path d="M22 30 L36 44 L50 23 L64 44 L78 30 L72 66 L77 80 H23 L28 66 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<circle cx="22" cy="25" r="6" fill="{accent}"/><circle cx="50" cy="17" r="6" fill="{accent}"/><circle cx="78" cy="25" r="6" fill="{accent}"/>'
        '<path d="M29 70 H71 M25 85 H75" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    ),
    chess.KING: (
        '<path d="M32 43 H68 L65 68 L78 80 H22 L35 68 Z" fill="{piece_fill}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M50 15 V39 M39 27 H61" stroke="{accent}" stroke-width="7" stroke-linecap="round"/>'
        '<path d="M29 51 H71 M27 85 H73" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    ),
}


def _piece_accent(ability):
    if ability in ("plague", "poison", "necromancer"):
        return "#8de15d"
    if ability in ("fire", "aura_kill", "titan", "dragon_breath"):
        return "#ff7043"
    if ability in ("freeze", "chrono", "shield"):
        return "#70d7ff"
    if ability in ("chaos", "assassin", "vampire"):
        return "#d58cff"
    if ability in ("blink", "demon_blink", "sniper", "laser"):
        return "#ffd166"
    return "#62e6c6"


def custom_piece_svg(piece, ability, square, cell_size):
    white = piece.color == chess.WHITE
    piece_fill = "#fff1ce" if white else "#29334b"
    ink = "#2d384e" if white else "#d7e5ff"
    accent = _piece_accent(ability)
    ability_label = "AI" if not white else ability.replace("unique_", "").replace("_", "").upper()
    opacity = "0.38" if ability == "stealth" else "1"
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    x = file * cell_size
    y = (7 - rank) * cell_size
    title = html.escape(f"{'White' if white else 'Black'} {chess.piece_name(piece.piece_type)} — {ability}", quote=True)
    if ability in POWER_DESCRIPTIONS:
        title = html.escape(
            f"{'White' if white else 'Black'} {chess.piece_name(piece.piece_type)} — "
            f"{POWER_DESCRIPTIONS[ability]}",
            quote=True,
        )
    art = PIECE_ART[piece.piece_type].format(piece_fill=piece_fill, ink=ink, accent=accent)
    return (
        f'<g transform="translate({x} {y}) scale({cell_size / 100})" '
        f'role="img" aria-label="{title}" opacity="{opacity}">'
        f'<title>{title}</title>'
        f'<circle cx="50" cy="52" r="43" fill="{ink}" opacity="0.18"/>'
        f'<circle cx="50" cy="49" r="39" fill="{piece_fill}" stroke="{accent}" stroke-width="4"/>'
        f'{art}'
        f'<circle cx="81" cy="79" r="12" fill="{ink}" stroke="{accent}" stroke-width="3"/>'
        f'<text x="81" y="83" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="{piece_fill}">{html.escape(ability_label)}</text>'
        '</g>'
    )


def render_custom_board(board, army, highlights=None, arrows=None, size=480):
    cell_size = size / 8
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="Custom chess board">'
    ]
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, 7 - rank)
            base = "#d9e3dc" if (file + rank) % 2 == 0 else "#425d6c"
            x, y = file * cell_size, rank * cell_size
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{base}"/>')
            if highlights and square in highlights:
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{highlights[square]}"/>')

    for square, piece in board.piece_map().items():
        ability_slot = {
            chess.PAWN: "p",
            chess.KNIGHT: "n",
            chess.BISHOP: "b",
            chess.ROOK: "r",
            chess.QUEEN: "q",
            chess.KING: "k",
        }.get(piece.piece_type)
        ability = army[ability_slot] if piece.color == chess.WHITE and ability_slot else "AI"
        parts.append(custom_piece_svg(piece, ability, square, cell_size))

    for start, end, color in arrows or []:
        start_x = (chess.square_file(start) + 0.5) * cell_size
        start_y = (7 - chess.square_rank(start) + 0.5) * cell_size
        end_x = (chess.square_file(end) + 0.5) * cell_size
        end_y = (7 - chess.square_rank(end) + 0.5) * cell_size
        dx, dy = end_x - start_x, end_y - start_y
        length = math.hypot(dx, dy) or 1
        unit_x, unit_y = dx / length, dy / length
        tip_x, tip_y = end_x - unit_x * cell_size * 0.18, end_y - unit_y * cell_size * 0.18
        base_x, base_y = tip_x - unit_x * cell_size * 0.22, tip_y - unit_y * cell_size * 0.22
        side_x, side_y = -unit_y * cell_size * 0.12, unit_x * cell_size * 0.12
        safe_color = html.escape(color, quote=True)
        parts.append(
            f'<line x1="{start_x}" y1="{start_y}" x2="{base_x}" y2="{base_y}" '
            f'stroke="{safe_color}" stroke-width="{cell_size * 0.12}" stroke-linecap="round" opacity="0.8"/>'
            f'<polygon points="{tip_x},{tip_y} {base_x + side_x},{base_y + side_y} '
            f'{base_x - side_x},{base_y - side_y}" fill="{safe_color}" opacity="0.9"/>'
        )

    parts.append("</svg>")
    return "".join(parts)


st.title("⚔️ Asymmetric Chess Army vs. Stockfish")
st.markdown(
    "Choose from **30 custom armies**. Every piece has a globally unique special move. "
    "Kings cannot be captured; games end only by checkmate, stalemate, or threefold repetition."
)

with st.sidebar:
    st.header("1. Stockfish Intelligence Mode")
    sf_mode = st.radio(
        "Does Stockfish know the custom rules?",
        ["Blind (Standard Chess Rules Only)", "Rule-Aware (Knows Your Army's Powers)"],
        index=0
    )
    sf_knows_rules = (sf_mode == "Rule-Aware (Knows Your Army's Powers)")

    st.header("2. Choose Your Army")
    army_options = {v["name"]: k for k, v in ARMIES.items()}
    selected_name = st.selectbox("Faction (30 Available):", list(army_options.keys()))
    army_id = army_options[selected_name]
    selected_army = ARMIES[army_id]
    st.info(f"**Abilities:** {selected_army['desc']}")
    st.caption("Each piece has a different special move, unique across all 30 armies.")
    with st.expander("How these powers work"):
        for label, slot in (
            ("Pawn", "p"), ("Knight", "n"), ("Bishop", "b"),
            ("Rook", "r"), ("Queen", "q"), ("King", "k")
        ):
            ability = selected_army[slot]
            st.markdown(f"**{label} — Unique move:** {POWER_DESCRIPTIONS[ability]}")

    st.header("3. Deploy Units (1, 2, 3+)")
    p_count = st.slider("Pawns", 0, 8, 8)
    n_count = st.slider("Knights", 0, 4, 1)
    b_count = st.slider("Bishops", 0, 4, 0)
    r_count = st.slider("Rooks", 0, 4, 0)
    q_count = st.slider("Queens", 0, 3, 0)

    roster = {
        chess.PAWN: p_count,
        chess.KNIGHT: n_count,
        chess.BISHOP: b_count,
        chess.ROOK: r_count,
        chess.QUEEN: q_count
    }
    roster_is_valid = n_count + b_count + r_count + q_count <= 7
    if not roster_is_valid:
        st.error("Only seven non-pawn units fit beside the King. Reduce the back-rank unit count.")

    st.header("4. Simulation Controls")
    search_depth = st.selectbox("Engine Search Depth", [1, 2, 3], index=1)
    move_delay = st.slider("Auto-Play Speed (sec/move)", 0.05, 1.5, 0.3)

    if st.button("🔄 Reset / Spawn New Army", use_container_width=True, type="primary", disabled=not roster_is_valid):
        st.session_state.game = AsymmetricBoard(selected_army, roster)
        st.session_state.sf_eval = "0.00 (Even)"
        st.session_state.sf_best_arrows = []
        st.session_state.move_count = 0
        st.session_state.review_mode = False
        st.session_state.review_index = 0
        st.rerun()
if "game" not in st.session_state:
    st.session_state.game = AsymmetricBoard(selected_army, roster)
    st.session_state.sf_eval = "0.00 (Even)"
    st.session_state.sf_best_arrows = []
    st.session_state.move_count = 0
    st.session_state.review_mode = False
    st.session_state.review_index = 0

game = st.session_state.game
if getattr(game, "army", {}).get("name") in {army["name"] for army in ARMIES.values()}:
    current_army = next(army for army in ARMIES.values() if army["name"] == game.army["name"])
    game.army = current_army
if not hasattr(game, "position_history"):
    legacy_game = game
    legacy_name = getattr(legacy_game, "army", {}).get("name")
    current_army = next((army for army in ARMIES.values() if army["name"] == legacy_name), selected_army)
    game = AsymmetricBoard(current_army)
    game.board = legacy_game.board.copy()
    game.plague_timers = getattr(legacy_game, "plague_timers", {}).copy()
    game.stun_timers = getattr(legacy_game, "stun_timers", {}).copy()
    game.captured_white = getattr(legacy_game, "captured_white", []).copy()
    game.event_log = getattr(legacy_game, "event_log", []).copy()
    game.position_history = []
    game.position_counts = {}
    game._record_position()
    st.session_state.game = game

if not hasattr(game, "position_counts"):
    game.position_counts = {}
    for snapshot in game.position_history:
        key = snapshot.get("position_key")
        if key is not None:
            game.position_counts[key] = game.position_counts.get(key, 0) + 1
    if not game.position_counts:
        game.position_history = []
        game._record_position()

if "review_mode" not in st.session_state:
    st.session_state.review_mode = False
if "review_index" not in st.session_state:
    st.session_state.review_index = 0

history = game.position_history
last_review_index = len(history) - 1
if game.is_game_over() and not st.session_state.review_mode:
    st.session_state.review_index = last_review_index
st.session_state.review_index = max(0, min(st.session_state.review_index, last_review_index))
review_state = history[st.session_state.review_index] if game.is_game_over() and st.session_state.review_mode else None
display_board = review_state["board"] if review_state else game.board
display_plague_timers = review_state["plague_timers"] if review_state else game.plague_timers
display_event_log = review_state["event_log"] if review_state else game.event_log

def step_turn():
    if game.is_game_over():
        return

    if game.board.turn == chess.WHITE:
        move, _ = get_best_custom_move(game, depth=search_depth, for_white=True)
        if move:
            game.push_custom_move(move, log_events=True)

    if not game.is_game_over() and game.board.turn == chess.BLACK:
        black_moves = game.get_custom_legal_moves()
        if not black_moves:
            return
        elif sf_knows_rules:
            sf_move, custom_ev = get_best_custom_move(game, depth=search_depth, for_white=False)
            if sf_move:
                black_perspective_eval = -custom_ev / 100.0
                st.session_state.sf_eval = f"{black_perspective_eval:+.2f} (Rule-Aware Eval)"
                st.session_state.sf_best_arrows = [(sf_move.from_square, sf_move.to_square, "#1687ff")]
                game.push_custom_move(sf_move, log_events=True)
        else:
            if not os.path.exists(STOCKFISH_PATH):
                st.error(f"Stockfish executable not found beside app.py: `{STOCKFISH_PATH}`")
                return

            engine = None
            engine_failed = False
            try:
                engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                engine_board = game.board.copy(stack=False)
                info = engine.analyse(engine_board, chess.engine.Limit(time=0.05))
                score = info["score"].black()
                if score.is_mate():
                    st.session_state.sf_eval = f"Mate in {score.mate()} (Delusional)"
                else:
                    cp = score.score() / 100.0
                    st.session_state.sf_eval = f"{cp:+.2f} (Blind Eval)"

                result = engine.play(engine_board, chess.engine.Limit(time=0.05), root_moves=black_moves)
                sf_move = result.move
                st.session_state.sf_best_arrows = [(sf_move.from_square, sf_move.to_square, "#e05252")]
                game.push_custom_move(sf_move, log_events=True)
            except chess.engine.EngineError as exc:
                engine_failed = True
                if black_moves:
                    fallback = random.choice(black_moves)
                    st.session_state.sf_best_arrows = [(fallback.from_square, fallback.to_square, "#e05252")]
                    game.push_custom_move(fallback, log_events=True)
                st.warning(f"Stockfish could not complete its move; using a legal fallback. Details: {exc}")
            finally:
                if engine:
                    try:
                        engine.quit()
                    except chess.engine.EngineTerminatedError as exc:
                        if not engine_failed:
                            st.warning(f"Stockfish exited before shutdown completed: {exc}")

        st.session_state.move_count += 1
col_main, col_side = st.columns([1.3, 1])

with col_main:
    st.subheader("🏰 True Battlefield (Real Rules & Statuses)")
    if review_state:
        st.caption(f"Reviewing position {st.session_state.review_index + 1} of {len(history)}.")
    squares_highlight = {sq: "#88cc4488" for sq in display_plague_timers}
    svg_main = render_custom_board(display_board, game.army, highlights=squares_highlight, size=480)
    st.markdown(f'<div style="display: flex; justify-content: center;">{svg_main}</div>', unsafe_allow_html=True)

with col_side:
    if sf_knows_rules:
        st.subheader("👁️ What Stockfish Sees (Rule-Aware)")
        st.caption("Stockfish sees plague zones (green) and calculates your custom powers.")
        sf_fill = {sq: "#88cc4488" for sq in display_plague_timers}
    else:
        st.subheader("🙈 What Stockfish Sees (Blind Mode)")
        st.caption("Stockfish sees ONLY ordinary chess pieces—no plague, no armor, no traps.")
        sf_fill = {}

    svg_mini = render_custom_board(
        display_board,
        game.army,
        highlights=sf_fill,
        arrows=[] if review_state else st.session_state.sf_best_arrows,
        size=280
    )
    st.markdown(f'<div style="display: flex; justify-content: center;">{svg_mini}</div>', unsafe_allow_html=True)

    st.divider()

    m1, m2 = st.columns(2)
    if review_state:
        m1.metric("Position", f"{st.session_state.review_index + 1}/{len(history)}")
        m2.metric("Stockfish Eval", "Replay")
    else:
        m1.metric("Move Number", st.session_state.move_count)
        m2.metric("Stockfish Eval", st.session_state.sf_eval)

    b1, b2 = st.columns(2)
    if b1.button("▶️ Step 1 Turn", use_container_width=True, disabled=game.is_game_over()):
        step_turn()
        st.rerun()

    auto_play = b2.toggle("⏩ Auto-Play Match", value=False, disabled=game.is_game_over())

    if game.is_game_over():
        res = game.result()
        if res == "1-0":
            st.success(f"🏆 VICTORY! {selected_army['name']} defeated Stockfish ({res})!")
        elif res == "0-1":
            st.error(f"💀 DEFEAT! Stockfish survived the siege ({res}).")
        else:
            draw_reason = game.game_over_reason().title()
            st.warning(f"🤝 DRAW — {draw_reason} ({res}).")

        st.subheader("🔎 Review Game")
        current_index = st.session_state.review_index if st.session_state.review_mode else last_review_index
        previous_col, next_col, final_col = st.columns(3)
        if previous_col.button("◀ Previous Move", disabled=current_index <= 0, use_container_width=True):
            st.session_state.review_mode = True
            st.session_state.review_index = current_index - 1
            st.rerun()
        if next_col.button("Next Move ▶", disabled=current_index >= last_review_index, use_container_width=True):
            st.session_state.review_mode = True
            st.session_state.review_index = current_index + 1
            st.rerun()
        if final_col.button("Final Position", disabled=not st.session_state.review_mode, use_container_width=True):
            st.session_state.review_mode = False
            st.session_state.review_index = last_review_index
            st.rerun()
        st.caption(f"Position {current_index + 1} of {len(history)} (including the starting position).")

    st.subheader("📜 Unique Move Log")
    if display_event_log:
        for event in reversed(display_event_log[-8:]):
            st.write(event)
    else:
        st.caption("No special abilities triggered yet.")

if auto_play and not game.is_game_over():
    time.sleep(move_delay)
    step_turn()
    st.rerun()

