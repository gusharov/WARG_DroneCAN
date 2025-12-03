import dronecan
from dronecan import to_yaml

# Create a NodeStatus message
msg = dronecan.uavcan.protocol.NodeStatus()

# Fill fields with realistic example values
msg.uptime = 123456           # in milliseconds
msg.vendor_specific_status_code = 42    # Arbitrary vendor-specific code
print("before packing:", msg)
# Pack the message into a binary payload
binary_payload = msg._pack()  # produces correctly encoded UAVCAN payload

print("Packed binary payload:", binary_payload)

# Now decode it back into a new NodeStatus instance
decoded_msg = dronecan.uavcan.protocol.NodeStatus()
decoded_msg._unpack(binary_payload)

# Print human-readable YAML
print(to_yaml(decoded_msg))