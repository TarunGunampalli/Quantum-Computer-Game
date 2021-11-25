import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit.visualization import (
    plot_histogram,
    plot_state_qsphere,
    plot_bloch_multivector,
    plot_bloch_vector,
)
from ipywidgets import interact, interactive, fixed, interact_manual, Button, Layout


def getCastedValue(cast, question, limits=None):
    val = input(question)
    while True:
        try:
            val = cast(val)
            if limits != None and (val < limits[0] or val >= limits[1]):
                raise Exception("Invalid Input")
            break
        except:
            val = input("Please enter a valid input: ")
    return val


# BOSS CLASS
class Boss:
    def __init__(self, num_qubits):
        self.gates = []
        self.n = num_qubits
        self.attack_limit = 0.1
        self.qc = QuantumCircuit(self.n)
        self.randomizeBoss()

    def randomizeBoss(self):
        gates = [
            self.qc.h,
            self.qc.x,
            self.qc.cx,
            self.qc.cu3,
        ]  #!! just a way to formally visualize our gates will delete later
        for i in range(np.random.randint(5)):
            gate_choice = np.random.randint(0, 4)
            a = np.random.randint(
                0, self.n
            )  # random integers for indices of the circuit
            b = np.random.randint(0, self.n)
            while b == a:
                b = np.random.randint(0, self.n)
            c = np.random.random(
                6
            )  # can't pass floats for range of np.random functions so just use 6 integer placeholder? OR 7
            d = np.random.random(6)
            e = np.random.random(6)

            # if gate_choice == 0:
            #   self.qc.h(a)
            # elif gate_choice == 1:
            #   self.qc.x(a)
            # elif gate_choice == 2:
            #   self.qc.cx(a,b)
            # elif gate_choice == 3:
            #   self.qc.cu3(c,d,e,a,b)

    def bossAttack(self):
        # accumulate boss probability per turn depending on character attributes(start at .01, increase exponenetially?)
        attack_prob = np.random.randint(0, self.attack_limit)
        self.attack_limit += np.random.randint(0, self.attack_limit)
        if attack_prob > 0.6:
            self.attack_limit = 0

    def characterAttack(self, attack, attackArgs):
        qc = self.qc
        gates = {
            "H": qc.h,
            "X": qc.x,
            "U": qc.u,
            "CNOT": qc.cx,
            "CU": qc.cu,
            "M": qc.measure,
        }
        if attack == "M":
            mx = QuantumRegister(self.n)
            c = ClassicalRegister(self.n)
            m = QuantumCircuit(mx)
            m += qc
            m.measure(mx, c)
            m.draw()
            backend = Aer.get_backend("qasm_simulator")
            job = execute(m, backend, shots=1024)
            result = job.result()
            counts = result.get_counts(m)
            print(counts)
            return list(counts.keys())[0]
        else:
            gates[attack](*attackArgs)

        # if quantum sandbox, draw circuit each time
        # qc.draw('mpl')
        # print statevector
        # if measure
        # return measured value

    def getState(self):
        result = ""
        probs = Statevector.from_instruction(self.qc).probabilities()
        for state in range(len(probs)):
            bformat = "{0:0" + str(self.n) + "b}"
            state_str = bformat.format(state)
            if probs[state] == 0:
                continue
            elif probs[state] == 1:
                return "|" + state_str + ">"
            coefficient = np.sqrt(probs[state])
            coefficient = "{0:.2f}".format(coefficient)
            result += coefficient + " |" + state_str + "> + "
        result = result[: len(result) - 3]
        return result


# CHARACTER CLASS
class Character:
    def __init__(self, name, boss):
        self.attacks = None
        self.name = name
        self.class_type = self.getClass()
        self.health = 100
        self.turn_count = 1
        self.boss = boss
        while self.class_type == None:
            self.class_type = self.getClass()

    def getClass(self):
        print()
        print("\nChoose your class " + self.name.upper() + ": \n")
        print(
            ".-------.-----------.----------------.---------.---------.\n| JOKER | ENTANGLER | QUANTUM EXPERT | GAMBLER | SANDBOX |\n'-------'-----------'----------------'---------'---------'"
        )
        char_class = input()
        # create array for attack choices (could change at each turn) maybe want to change it so that our attack arrays are strings and just placeholders for charAttack
        if char_class.lower().strip() == "joker":
            self.attacks = None
            return "JOKER"
        elif char_class.lower().strip() == "entangler":
            self.attacks = ["H", "X", "CNOT", "M"]
            return "ENTANGLER"
        elif (
            char_class.lower().strip() == "god"
            or char_class.lower().strip() == "quantum expert"
        ):
            self.attacks = ["U", "CU", "M"]
            return "QUANTUM EXPERT"
        elif char_class.lower().strip() == "gambler":
            self.attacks = ["M"]
            return "GAMBLER"
        elif char_class.lower().strip() == "sandbox":
            self.attacks = ["M", "H", "X", "CNOT", "CU"]
            return "SANDBOX"
        else:
            print("Please input a valid character")

    def getAttacks(self):
        allAttacks = ["H", "X", "U", "CNOT", "CU", "M"]
        if self.class_type == "JOKER":
            self.attacks = np.random.choice(allAttacks, size=3, replace=False)
        return self.attacks

    def getAttackArgs(self, attack):
        result = []
        if attack == "H" or attack == "X":
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want to apply this gate to? (0 - {self.n - 1})\n",
                    (0, self.n),
                )
            )
        elif attack == "U":
            result.append(getCastedValue(float, "What theta do you want to apply?\n"))
            result.append(getCastedValue(float, "What phi do you want to apply?\n"))
            result.append(getCastedValue(float, "What lamba do you want to apply?\n"))
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want to apply this gate to? (0 - {self.n - 1})\n",
                ),
                (0, self.n),
            )
        elif attack == "CNOT":
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want as a control? (0 - {self.n - 1})\n",
                    (0, self.n),
                )
            )
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want as a target? (0 - {self.n - 1})\n",
                    (0, self.n),
                )
            )
            while result[0] == result[1]:
                result[1] = getCastedValue(
                    int, "Target can't be the same as the control: \n", (0, self.n)
                )
        elif attack == "CU":
            result.append(getCastedValue(float, "What theta do you want to apply?\n"))
            result.append(getCastedValue(float, "What phi do you want to apply?\n"))
            result.append(getCastedValue(float, "What lamba do you want to apply?\n"))
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want as a control? (0 - {self.n - 1})\n",
                    (0, self.n),
                )
            )
            result.append(
                getCastedValue(
                    int,
                    f"What qubit do you want as a target? (0 - {self.n - 1})\n",
                    (0, self.n),
                )
            )
            while result[3] == result[4]:
                result[4] = getCastedValue(
                    int, "Target can't be the same as the control: \n", (0, self.n)
                )
        elif attack == "M":
            result = []
        else:
            return None
        return result

    def getAttack(self):  # gets attack choice from player
        attacks = self.getAttacks()
        print()
        for i in range(len(attacks)):
            print(str(i + 1) + ": " + attacks[i])
        choice = getCastedValue(
            int,
            "\nHow do you want to attack? (1-" + str(len(attacks)) + ")\n",
            (1, len(self.attacks) + 1),
        )
        # while choice < 1 or choice > len(attacks):
        #   choice = input("Please enter a valid input: ")
        return attacks[choice - 1], self.getAttackArgs(attacks[choice - 1])

    # Attack choices H, X, CNOT, then choices = ["H", "X", "CNOT"]
    # asks for input out of attack choices and gets response
    # get qubit they want to operate on
    # dictionary of gates = {"H": qc.h,  "X": qc.x, "CNOT": qc.cx}
    # character ascii art (extra)


# GAME CLASS
class Game:
    def __init__(self):
        name = input(
            ".----------------------------------. \n| What is your name, quantum hero? |\n'----------------------------------'\n"
        )
        print()
        difficulty = getCastedValue(
            int,
            "/ \-----------------------------------, \n\_,|                                  | \n   |    Enter your difficulty level   | \n   |----------------------------------'\n\_/________________________________/\n",
            (1, 4),
        )
        self.num_qubits = difficulty + 1
        self.boss = Boss(self.num_qubits)
        self.character = Character(name, self.num_qubits)
        stop = False
        while not stop:  # break on measure or die
            stop, measurement = self.turn()
            if stop:
                print(measurement)

    def turn(self):
        attack, args = self.character.getAttack()
        measurement = self.boss.characterAttack(attack, args)
        if attack == "M":
            return True, measurement
        print("Current Boss State")
        print(self.boss.getState())
        print()

        return False, 1

        # execute gate attack
        # bossAttack()


game = Game()

# to do list: 1. make sure measure gates actually apply and shut down game when all measurement are done
# 2. Print statevectors each time for given class. Find a way to turn statevector in a more presentable fashion
# 3. interactive buttons for the game
# 4. Health bars- default set to 100, can change to customize classes with health bars and amount of times you can attack per turn.
# 5. Ascii Art
