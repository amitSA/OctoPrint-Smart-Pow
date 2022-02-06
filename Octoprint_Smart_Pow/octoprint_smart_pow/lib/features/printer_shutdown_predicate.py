



def printer_ready_to_shutdown(self, printer, temperature_threshold = 40):
    """
    Return whether the printer is ready to be turned off
    """
    temp_data = printer.get_current_temperatures()
    return temp_data["bed"] < temperature_threshold and temp_data["tool"] < temperature_threshold
