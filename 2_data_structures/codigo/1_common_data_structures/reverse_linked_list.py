class Solution(object):
    def reverseList(self, head):
        """
        :type head: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        prev_pointer, next_pointer, curr_pointer=None, None, head
        while curr_pointer:
            next_pointer=curr_pointer.next
            curr_pointer.next=prev_pointer
            prev_pointer=curr_pointer
            curr_pointer=next_pointer
        head=prev_pointer
        return head