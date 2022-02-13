import octoprint


def printer_ready_to_shutdown(
    printer: octoprint.printer.PrinterInterface, temperature_threshold=40
):
    """
    Return whether the printer is ready to be turned off
    """
    temp_data = printer.get_current_temperatures()
    if "bed" not in temp_data:
        return False
    # XXX maybe generalize to fetch all tools , which is possible if all tool keys are numbered.
    return (
        temp_data["bed"]["actual"] < temperature_threshold
        and temp_data["tool0"]["actual"] < temperature_threshold
    )
