# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def mergeTwoLists(self, list1: [ListNode], list2: [ListNode]) -> [ListNode]:
        list3 = ListNode()
        head = list3
        if not list1 and not list2:
            return

        while list1 and list2:
            if list1.val <= list2.val:
                list3.next = list1
                list3 = list3.next
                list1 = list1.next
            elif list2.val < list1.val:
                list3.next = list2
                list3 = list3.next
                list2 = list2.next
        while list1:
            list3.next = list1
            list3 = list3.next
            list1 = list1.next
        while list2:
            list3.next = list2
            list3 = list3.next
            list2 = list2.next
        return head.next
