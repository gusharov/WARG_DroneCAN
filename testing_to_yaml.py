import dronecan

binary_payload = "00000000000000000000000000000000100000010000000000000000"

print("before packing:", binary_payload)

# --- THE FIX STARTS HERE ---
# _unpack cannot read bytes. We must convert bytes to a list of bits (integers).
# This creates a list of 56 items (bits) from your 7 bytes.
msg = dronecan.ardupilot.gnss.Status()
#msg = dronecan.uavcan.protocol.NodeStatus()
print("drone packing:", msg)

msg._unpack(binary_payload) 

print("after unpacking", dronecan.to_yaml(msg))