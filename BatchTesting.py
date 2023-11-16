

'''
@brief
By passing a function pointer and two equal-length
lists of inputs and outputs, this function can batch
test the desired function pointer and print results.

@input funcPtr
The name of the function to test. Ie if testing the
function foobar(), simply pass the name without
parenthesis or inputs to the function, ie 'foobar'.

@input inputs
A list of inputs to be passed to the function. Works
perfectly well for functions with multiple inputs or
list inputs. Ie for the function add(i1, i2), each
entry in the 'inputs' list should contain two numeric
types. For instance, [[1, 2], [3, 4]] will run two tests
on the function with inputs '1, 2' and '3, 4'
respectively. Can use multiple sublists as list inputs
or scalars for single-input functions.

@input outputs
In the same format as the inputs list, this must be a
list of expected outputs exactly as they should appear.
If expecting one integer output from three separate tests,
this list should look like: [int, int, int]. If expecting
a list of three integer outputs from one test, the list 
should take the form [[int, int, int]].

@input printPasses
If true, the system will confirm the expected and actual
outputa on all successful tests via a console print.

@input printFails
If true, the system will confirm the expected and actual
outputs on all failed tests via a console print.
'''
def batchTest(funcPtr,
              inputs: list,
              outputs: list,
              printPasses=False,
              printFails=True) -> list:
    
    assert(len(inputs) == len(outputs))

    from Lib import printHeading


    printHeading(f"Batch testing function: '{funcPtr.__name__}'")
    testsPassed = 0


    # run the tests and record outputs
    for i, input in enumerate(inputs):
        if isinstance(input, list):
            output = funcPtr(*input)
        else:
            output = funcPtr(input)

        expectedOutput = outputs[i]

        # check if actual vs expected outputs match
        if output == expectedOutput:
            testsPassed += 1

            if printPasses:
                print(f"Test {i + 1}   [passed]")
                print(f"  :expected output: -> {outputs[i]}")
                print(f"  :measured output: -> {output}\n")
        else:
            if printFails:
                print(f"Test {i + 1}   [failed]")
                print(f"  :expected output: -> {outputs[i]}")
                print(f"  :measured output: -> {output}\n")

    printHeading(f"Tests passed: {testsPassed}/{len(inputs)}")



'''
@brief
Times function exectuion on a variable number of tests. Assumes
function only executes trivial, isolated code.
'''
def timeFunc(funcPtr, inputs: list, numTests, decimalAccuracy: int = 6):
    assert(isinstance(inputs, list))
    assert(numTests > 0)

    from numpy import mean
    from time import time
    from Lib import printHeading, closeto


    # execute main control code
    testStartTime = time()
    times = []

    for i in list(range(numTests)):
        start = time()

        funcPtr(*inputs)

        runtime = time() - start
        times.append(runtime)


    # first run is always an outlier. Discard
    times = times[1:]

    # calculate runtime diagnostis
    avgTime = mean(times)

    printHeading(f"Timing: {funcPtr.__name__} for {numTests} tests")

    print(f" - avg runtime:   {round(avgTime,    decimalAccuracy)}")
    print(f" - max runtime:   {round(max(times), decimalAccuracy)}")
    print(f" - min runtime:   {round(min(times), decimalAccuracy)}")
    print(f" - total runtime: {round(time() - testStartTime, decimalAccuracy)}")

    standardDeviation = sum( [(avgTime - t)**2 for t in times] )/numTests
    print(f" - standard deviation: {round(standardDeviation, decimalAccuracy)}")

    print()
    print("*units are in seconds")
    print("*total runtime includes additional function overhead")
    print()




def add(a, b):
    return a + b

if __name__ == '__main__':
    test1 = [1, 2]
    result1 = 3

    test2 = [-4, 12]
    result2 = 8
    
    test3 = [0, 1787]
    result3 = 85

    batchList = [test1, test2, test3]
    results = [result1, result2, result3]

    batchTest(add, batchList, results, printPasses=True)