from fastapi import status


# code : [message, response http code]
messages = {
    1001: ["Caption Generated Successfully.", status.HTTP_201_CREATED,True],
    1005: ["Something Went Wrong.", status.HTTP_400_BAD_REQUEST,False],
}