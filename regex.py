from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

class StartState(State):
    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False

class TerminationState(State):
    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False

class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return True

class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return self.curr_sym == curr_char

class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = []
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)

class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = []
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)

class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            new_state = self.__init_next_state(char, prev_state, tmp_next_state)

            if char in ["*", "+"]:
                if tmp_next_state in prev_state.next_states:
                    prev_state.next_states.remove(tmp_next_state)
                prev_state.next_states.append(new_state)
                tmp_next_state = new_state
            else:
                prev_state = tmp_next_state
                tmp_next_state = new_state
                prev_state.next_states.append(tmp_next_state)

        tmp_next_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()

            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, text: str) -> bool:
        def match(state: State, idx: int) -> bool:
            if isinstance(state, TerminationState):
                return idx == len(text)

            if isinstance(state, (StartState, StarState)):
                for nxt in state.next_states:
                    if nxt is not state and match(nxt, idx):
                        return True

            if idx < len(text) and state.check_self(text[idx]):
                for nxt in state.next_states:
                    if match(nxt, idx + 1):
                        return True

            return False

        return match(self.curr_state, 0)

if __name__ == "__main__":
    print("--- Test 1: a*4.+hi ---")
    regex_compiled = RegexFSM("a*4.+hi")
    print(regex_compiled.check_string("aaaaaa4uhi")) #True
    print(regex_compiled.check_string("4uhi"))       #True
    print(regex_compiled.check_string("meow"))       #False

    print("\n--- Test 2: a+b+c+ ---")
    re2 = RegexFSM("a+b+c+")
    print(re2.check_string("abc"))         # True
    print(re2.check_string("aaabbcccc"))   # True
    print(re2.check_string("ac"))          # False
    print(re2.check_string("abbc"))        # True

    print("\n--- Test 3: ok.* ---")
    re3 = RegexFSM("ok.*")
    print(re3.check_string("ok"))          # True
    print(re3.check_string("ok12345"))     # True
    print(re3.check_string("ok!@#"))       # True
    print(re3.check_string("o"))           # False

    print("\n--- Test 4: x*y*z* ---")
    re4 = RegexFSM("x*y*z*")
    print(re4.check_string(""))            # True
    print(re4.check_string("xyz"))         # True
    print(re4.check_string("xxxxzz"))      # True
    print(re4.check_string("xa"))          # False

    print("\n--- Test 5: 1.x+0 ---")
    re5 = RegexFSM("1.x+0")
    print(re5.check_string("1ax0"))        # True
    print(re5.check_string("1 xxxx0"))     # True
    print(re5.check_string("1x0"))         # False
    print(re5.check_string("1ax"))         # False

    print("\n--- Test 6: ..+ ---")
    re6 = RegexFSM("..+")
    print(re6.check_string("hi"))          # True
    print(re6.check_string("python"))      # True
    print(re6.check_string("a"))           # False
