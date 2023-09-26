a = "GET_/path"

a, b = a.split('_')
print(a, b)


# from pydantic import BaseModel


# class Response(BaseModel):
#     data: dict | list | None = None
#     status: int
#     ui_message: list[str] | None = []

# test_dict = {"test":"hi"}
# test_list = [1,2,34]

# resp = Response(data=test_list, status=200, ui_message=['hello'])


# print(resp.model_dump())





# from collections import deque

# example = deque([], maxlen=3)

# # example.pop(0)
# example.append(1)
# example.append(2)
# example.append(3)
# example.append(4)

# if example:
#     print(sum(example) / len(example))