# Recursion over a tree: folder sizes

--- teach
### The pattern: a tree of nested dicts wants recursion
"Given a disk-usage tree, report the total size of every folder." A brute force flattens every file to its full path, then, for each folder, adds up the files whose path starts with the folder's path.
```python
def dir_sizes_slow(tree):
    files = []                                   # (path, size)
    folders = ["/"]
    def collect(node, path):
        for name, child in node.items():
            full = path.rstrip("/") + "/" + name
            if isinstance(child, dict):
                folders.append(full); collect(child, full)
            else:
                files.append((full, child))
    collect(tree, "/")
    return {f: sum(s for p, s in files if p.startswith(f.rstrip("/") + "/"))
            for f in folders}
```
Every folder rescans every file. The pattern: a folder's size is its files plus the sizes of its subfolders, and that sentence *is* a recursive function.

--- quiz
A tree has F folders and N files. What does the flatten-then-filter brute force cost?
- [ ] O(N + F): each node once
- [x] O(F · N): every folder scans every file
- [ ] O(N log N): the paths are sorted
> The dict comprehension runs one `sum` over all N files for each of the F folders. With 3,061 folders and 3,000 files that is nine million path checks instead of six thousand visits.

--- teach
### The insight: return the total, record it on the way out
A helper walks one folder. For each child: if it is a dict, recurse and add what comes back; otherwise it is a file, add its size. Record the folder's total before returning it.
```python
def dir_sizes(tree):
    out = {}
    def walk(node, path):
        total = 0
        for name, child in node.items():
            if isinstance(child, dict):
                total += walk(child, path.rstrip("/") + "/" + name)
            else:
                total += child
        out[path] = total
        return total
    walk(tree, "/")
    return out
```
Every node is visited exactly once.

--- code
Write the body of `walk`: add up the ints, recurse into dict children with the joined path, record the total in `out[path]`, and return it. Then call `walk(tree, "/")` and print `out["/"]`.
```python
out = {}
tree = {"Users": {"jdoe": 5}, "swapfile": 10}
def walk(node, path):
```
expect: 15
check: out["/Users"] == 5
solution:     total = 0
solution:     for name, child in node.items():
solution:         if isinstance(child, dict):
solution:             total += walk(child, path.rstrip("/") + "/" + name)
solution:         else:
solution:             total += child
solution:     out[path] = total
solution:     return total
solution: walk(tree, "/")
solution: print(out["/"])
> `Users` is a folder, so `walk` recurses, records `out["/Users"] = 5` and returns 5. The root adds the 10-byte swapfile and records 15. The body is indented four spaces; the two calls after it are not.

--- predict
What does this print?
```python
def total(node):
    return sum(total(v) if isinstance(v, dict) else v for v in node.values())

print(total({"a": 1, "b": {"c": 2, "d": {"e": 3}}}))
```
answer: 6
> `a` is a file of 1. `b` is a folder: `c` is 2, and `d` is a folder holding `e`, 3. So `b` is 5 and the root is 1 + 5 = 6. The recursion bottoms out at plain ints.

--- teach
### Paths, empty folders, and the mutable-default trap
The root is `"/"`, and children join with a single slash: `path.rstrip("/") + "/" + name` gives `/Users`, not `//Users`. An empty folder `{}` still gets visited, so `out["/Library"] = 0` appears; files never do. An empty tree gives `{"/": 0}`.

Interviewers love this one: never write `def dir_sizes(tree, out={})`. A default value is created once and shared by every call, so the second call would return the first call's folders too. Use `out=None` and create the dict inside, or, as above, a nested helper.

--- code
Set `child` to the path of folder `name` inside `path`, joined with a single slash, and print it.
```python
path = "/"
name = "Users"
```
expect: /Users
check: child == "/Users"
solution: child = path.rstrip("/") + "/" + name
solution: print(child)
> `rstrip("/")` turns the root `"/"` into `""`, so the join gives `/Users` and not `//Users`. For `path = "/Users"` nothing is stripped and the result is `/Users/jdoe`.

--- fill
Complete the test that tells a subfolder from a file.
```python
if isinstance(child, ___):
    total += walk(child, path.rstrip("/") + "/" + name)
else:
    total += child
```
answer: dict
> A folder is a nested dict; a file is an int. `isinstance` is the standard way to branch on type; `type(child) == dict` also works but is less idiomatic.

--- quiz
What is wrong with `def dir_sizes(tree, out={}):`?
- [ ] `out` cannot be a dict; it must be a list
- [x] The same dict is reused by every call, so results leak between calls
- [ ] Python raises `SyntaxError` on a mutable default
> Default arguments are evaluated once, when `def` runs. Every call without `out` shares that one dict. The fix is `out=None` and `out = {} if out is None else out` inside.

--- teach
### Depth, and how to say it
O(number of files and folders) time, each visited once; O(depth) call stack plus O(folders) for the result.

Say it out loud: "A folder's size is its files plus its subfolders, so I recurse and record each total on the way back up. Every node is visited once. CPython's recursion limit is about 1,000 frames; for a deeper tree I would keep an explicit stack of `(path, node)` pairs and sum children before parents."

The tests nest 200 deep, so recursion is safe here, but be ready to describe the iterative rewrite.

--- exercise 12.8

--- recap
- Nested dicts are a tree; "size of a folder = files + subfolders" is a recursive function.
- Recurse on dict children, add int children, record the total, return it.
- Join paths with `path.rstrip("/") + "/" + name`; empty folders are still listed.
- Never use a mutable default like `out={}`; know the explicit-stack rewrite for deep trees.
