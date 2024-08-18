def is_internal(name: str) -> bool:
    """Check if a function / method / class name indicate if it's internal."""
    return name.startswith("_")
