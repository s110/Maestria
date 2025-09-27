#1 sorting
class Solution:
    def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
        row_strength = [(sum(row), i) for i, row in enumerate(mat)]
        row_strength.sort(key=lambda x: (x[0], x[1]))
        return [row[1] for row in row_strength[:k]]

#Min_heap
import heapq
class Solution:
    def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
        heap = []
        for i, row in enumerate(mat):
            strength = sum(row)
            heapq.heappush(heap, (-strength, -i))
            if len(heap) > k:
                heapq.heappop(heap)
        return [-i for _, i in sorted(heap, reverse=True)]

#binary search + heap
class Solution:
    def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
        def binarySearch(arr):
            left, right = 0, len(arr) - 1
            while left <= right:
                mid = (left + right) // 2
                if arr[mid] == 1:
                    left = mid + 1
                else:
                    right = mid - 1
            return left

        queue = [(binarySearch(row), idx) for idx, row in enumerate(mat)]
        heapq.heapify(queue)

        return [idx for _, idx in heapq.nsmallest(k, queue)]