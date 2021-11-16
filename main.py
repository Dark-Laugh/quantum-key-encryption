"""
@author rpthi
"""
from CommunicationChannel import QKAChannel

security_level = 0.5  # level of security from (0-1]
qkaChannel = QKAChannel(security_level)
qkaChannel.print_results()
