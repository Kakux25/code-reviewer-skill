from prices import quote


def checkout(request):
    return {"total": quote(request["amount"], request.get("discount", 0))}
