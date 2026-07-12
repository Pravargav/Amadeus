## Tensors vs Vectors(multi-dim)

- 1d vector [a]
- 2d vector [a, b]
- 3d vector [a, b, c]
...
- nd vector [a, b, c, d....n dimensions]

i.e. Collection of vectors is tensor
[ ndv1, ndv2, ndv3, ..... ]

Note: "A collection (or ordered list) of n-dimensional vectors can be represented as a tensor."

That's a great question. The key reason is that **PyTorch and TensorFlow are not designed only for vectors**. They need a data structure that works for *any number of dimensions*. The word **tensor** already has that meaning in mathematics.

Think of it this way:

| Data                | Shape    | Mathematical name | PyTorch/TensorFlow |
| ------------------- | -------- | ----------------- | ------------------ |
| `5`                 | `()`     | Scalar            | Tensor             |
| `[1, 2, 3]`         | `(3,)`   | Vector            | Tensor             |
| `[[1,2],[3,4]]`     | `(2,2)`  | Matrix            | Tensor             |
| `(32, 224, 224)`    | 3D array | Rank-3 tensor     | Tensor             |
| `(64, 3, 224, 224)` | 4D array | Rank-4 tensor     | Tensor             |

Notice that **not everything is a collection of vectors**.

For example, an RGB image has shape `(224, 224, 3)`.

What is it?

* Not a vector.
* Not a collection of vectors in any unique mathematical sense. You could interpret it as a collection of rows, columns, or pixels.
* It is naturally described as a **rank-3 tensor**.

Similarly, a batch of videos might have shape:

```
(batch, frames, height, width, channels)
```

For example:

```
(32, 16, 224, 224, 3)
```

Calling this a "collection of vectors" would be awkward and ambiguous.

### Why the name "tensor"?

PyTorch and TensorFlow implement **N-dimensional arrays**.

A tensor is simply:

> **An array with any number of dimensions (rank).**

Examples:

```
0-D Tensor → 5
1-D Tensor → [1,2,3]
2-D Tensor → [[1,2],[3,4]]
3-D Tensor → [[[...]]]
4-D Tensor → Batch of images
5-D Tensor → Batch of videos
```

Instead of inventing names like:

* ScalarArray
* VectorArray
* MatrixArray
* CubeArray
* HyperCubeArray

they use one universal term: **Tensor**.

### Why not call it a "collection of vectors"?

Suppose you have a tensor of shape:

```
(4, 5, 6)
```

Is it

* 4 collections of 5 vectors of length 6?
* 5 collections of 4 vectors of length 6?
* 6 collections of 4 vectors of length 5?

All of these interpretations are possible depending on which axis you choose.

The tensor itself doesn't prescribe a particular interpretation—it is simply a multidimensional array with shape `(4, 5, 6)`.

### Historically

The term "tensor" wasn't invented by PyTorch or TensorFlow. It comes from mathematics and physics, where tensors generalize:

* Scalars (rank 0)
* Vectors (rank 1)
* Matrices (rank 2)
* Higher-dimensional objects (rank 3 and above)

Machine learning adopted the same terminology because neural networks manipulate these kinds of multidimensional arrays all the time.

So when you write in PyTorch:

```python
x = torch.tensor([[1, 2], [3, 4]])
```

`x` happens to be a **2D tensor** (a matrix). If you instead create:

```python
x = torch.tensor(5)
```

it's a **0D tensor** (a scalar). The name `tensor` is broad enough to cover both, which is why frameworks use it as the universal data type.

- https://youtu.be/f5liqUk0ZTw?si=KIZ1pmm-bo2pJsKW

- https://youtu.be/1GwAEnegaRs?si=qG3jKOouKanykPGo
