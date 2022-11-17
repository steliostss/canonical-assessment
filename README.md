# Canonical Interview - Technical Assessment

Technical Assessment for the Canonical Interview process, to test knowledge of linux packaging

## Implementation

### Implementing command line argument parsing

To manage the command line arguments I used the [Argparse](https://docs.python.org/3/library/argparse.html)
Python library. I added were 2 arguments in total, with the main argument being *arch* as defined by
the assignment, and the other being *N* which defines the top N elements selection.

```python
# architecture argument
argparser.add_argument("arch", nargs=1, default="",
                        type=str, help="Accepted architectures: ...")

# top N elements
argparser.add_argument("-n", default=10, type=int, nargs=1,
                        help="Get the top-N packages. Default 10.")
```

### Download and read file

I used the python library [urllib](https://docs.python.org/3/library/urllib.request.html) to download
the file and [gzip](https://docs.python.org/3/library/gzip.html) to read its' compressed contents line-by-line.
For each line I striped the extra spaces and then splitted  it by the remaining space character. This gave me
a list L of 2 elements: ```L[0]: file``` and ```L[1]: List of packages```. I splitted the list of packages
using the comma as separator as defined by the documentation. 

### Counting occurences

I used a dictionary since it is easy to keep key-value pairs and both inserting and accessing
elements is of O(1) complexity.
```python
# add an occurence if *pkg* doesn't exist or just increment by 1
package_dict[pkg] = package_dict[pkg] + 1 if (pkg in package_dict) else 1
```

### Finding the top-10

I selected the top 10 elements with most occurences using the
[heapq.nlargest](https://docs.python.org/3/library/heapq.html#heapq.nlargest) python function.

#### Complexity

The complexity of this function is of **O(N*log(T))**, where:
- N: the number of total elements
- T: the top <T> elements

#### Explanation:

- For building the heap for first K elements will be done K*log(K)
- For pushing and popping, the remaining elements will be done in (N-K)*log(K)
- The overall time complexity will be N*log(K)

#### Thought behind selection:

Sorting and then selecting the top K (10 in our case) elements would be the
most obvious choice, firstly for readability and secondly for simplicity.
But the amount of lines in the contents file is unknown and probably large,
that is why I opted for this algorithm, since it's complexity is basically
is of **O(N)** since O(log10) = O(1).

### Memory management

In order to manage memory effectively with minimal effort I used the
[tempfile](https://docs.python.org/3/library/tempfile.html) library to assist
me in creating a temporary directory to store the file.

## Time Spent

The time spent on this assessment was roughly 8-hours in total, which includes
studying the Debian repository format.

## Author

[Stelios Tsagkarakis](https://github.com/steliostss)

