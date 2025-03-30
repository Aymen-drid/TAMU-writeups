import hashlib
from z3 import *

class Brain:
    def __init__(self, neurons):
        self.neurons = neurons
        self.thought_size = 10
        
    def brainstem(self):
        return hashlib.sha256(",".join(str(x) for x in sum(self.neurons, [])).encode()).hexdigest()
        
    def rot(self, data):
        for i in range(len(data)):
            self.neurons[(3 * i + 7) % self.thought_size][(9 * i + 3) % self.thought_size] ^= data[i]
            
    def think(self, data):
        thought = [0] * self.thought_size
        for i in range(self.thought_size):
            thought[i] = sum(self.neurons[i][j] * data[j] for j in range(self.thought_size))
        self.neurons[:-1] = self.neurons[1:]
        self.neurons[-1] = thought
        return thought

# Initialize the brain with the values from the challenge
healthy_brain = [[71, 101, 18, 37, 41, 69, 80, 28, 23, 48], 
                 [35, 32, 44, 24, 27, 20, 34, 58, 24, 9], 
                 [73, 29, 37, 94, 27, 58, 104, 65, 116, 44], 
                 [26, 83, 77, 116, 9, 96, 111, 118, 52, 62], 
                 [100, 15, 119, 53, 59, 34, 38, 68, 104, 110], 
                 [51, 1, 54, 62, 56, 120, 4, 80, 60, 120], 
                 [125, 92, 95, 98, 97, 110, 93, 33, 128, 93], 
                 [70, 23, 123, 40, 75, 23, 104, 73, 52, 6], 
                 [14, 11, 99, 16, 124, 52, 14, 73, 47, 66], 
                 [128, 11, 49, 111, 64, 108, 14, 66, 128, 101]]

brainrot = b"gnilretskdi ,coffee ,ymotobol ,amenic etulosba ,oihO ni ylno ,oihO ,pac eht pots ,pac ,yadot yarp uoy did ,pu lio ,eohs ym elkcub 2 1 ,sucric latigid ,zzir tanec iaK ,tac frumS ,yzzilg ,ekahs melraH ,tanec iaK ,raebzaf ydderF ,gnixamnoog ,hoesac ,relzzir eht rof ttayg ruoy tuo gnikcits ,reppay ,gnippay ,pay ,gniggom ,gom,ttalcobmob ,gnillihc gnib ,deepswohsi ,tor niarb ,oitar + L ,ozob L ,L ,oitar ,ie ie iE ,suoived ,emem seimmug revas efil dna seceip s'eseeR ,io io io ,ytrap zzir koTkiT ,teggun ,su gnoma ,retsopmi ,yssus ,suS ,elgnid eladnuaQ ,gnos metsys ym ni atnaF ,kcil suoived ,syddid ta sthgin 5 ,hsinapS ro hsilgnE .gnos teksirb ,agnizab ,bruc eht etib ,orb lil ,dulb ,ni gnihcram og stnias eht nehw ho ,neerb fo seert ees I ,sinneD ekud ,biks no ,ennud yvvil ,knorg ybab ,rehtorb pu s'tahw ,gab eht ni seirf eht tuP ,edaf repat wol ,yddid ,yddirg ,ahpla ,gnixxamskool ,gninoog ,noog ,egde ,gnigde ,raeb evif ydderf ,ekahs ecamirg ,ynnacnu ,arua ,daeh daerd tnalahcnon ,ekard ,gnixat munaF ,xat munaf ,zzir idibikS ,yug llihc ,eiddab ,kooc reh/mih tel ,gnikooc ,kooc ,nissub ,oihO ,amgis eht tahw ,amgis ,idibikS no ,relzzir ,gnizzir ,zzir ,wem ,gniwem ,ttayg ,teliot idibikS ,idibikS"[::-1]

# Apply the rot transformation
brain = Brain([row[:] for row in healthy_brain])  # Make a deep copy
brain.rot(brainrot)

required_thoughts = [
    [59477, 41138, 59835, 73146, 77483, 59302, 102788, 67692, 62102, 85259],
    [40039, 59831, 72802, 77436, 57296, 101868, 69319, 59980, 84518, 73579466],
    [59783, 73251, 76964, 58066, 101937, 68220, 59723, 85312, 73537261, 7793081533],
    [71678, 77955, 59011, 102453, 66381, 60215, 86367, 74176247, 9263142620, 982652150581],
]

# We need to solve for each chunk of 10 bytes
flag = bytearray(40)

# Let's use Z3 to solve the constraints for each 10-byte chunk
for chunk_index in range(4):
    # Get the current state of the neurons for this chunk
    current_brain = Brain([row[:] for row in brain.neurons])
    
    # Create Z3 solver
    solver = Solver()
    
    # Create symbolic variables for the 10 bytes of the flag chunk
    flag_chunk = [BitVec(f'flag_{chunk_index}_{i}', 8) for i in range(10)]
    
    # Constrain each byte to printable ASCII range
    for i in range(10):
        solver.add(flag_chunk[i] >= 32)
        solver.add(flag_chunk[i] <= 126)
    
    # Calculate the expected thought for this chunk
    expected_thought = required_thoughts[chunk_index]
    
    # Create the constraint equations based on the think method
    thought = [0] * current_brain.thought_size
    for i in range(current_brain.thought_size):
        thought_expr = 0
        for j in range(current_brain.thought_size):
            thought_expr += current_brain.neurons[i][j] * flag_chunk[j]
        solver.add(thought_expr == expected_thought[i])
    
    # Check if the constraints are satisfiable
    if solver.check() == sat:
        # Get the model (solution)
        model = solver.model()
        # Extract the solution bytes
        for i in range(10):
            flag[chunk_index * 10 + i] = model[flag_chunk[i]].as_long()
        
        # Apply the think operation to update the brain state for the next chunk
        brain.think([model[flag_chunk[i]].as_long() for i in range(10)])
    else:
        print(f"No solution found for chunk {chunk_index}")
        exit(1)

solved_flag = bytes(flag)
print(f"Found flag: {solved_flag.decode()}")

# Verify solution
brain = Brain([row[:] for row in healthy_brain])
brain.rot(brainrot)

failed_to_think = False
for i in range(0, len(solved_flag), 10):
    thought = brain.think(solved_flag[i:i + 10])
    if thought != required_thoughts[i//10]:
        failed_to_think = True
        print(f"Verification failed for chunk {i//10}")

if failed_to_think or brain.brainstem() != "4fe4bdc54342d22189d129d291d4fa23da12f22a45bca01e75a1f0e57588bf16":
    print("Solution is incorrect")
else:
    print("Solution verified! Flag is correct")
