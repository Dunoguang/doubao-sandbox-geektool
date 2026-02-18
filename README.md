We know that Doubao (an AI tool) can use an agent to run Python code online. So, can we use its server?

Yes — the Python platform in Doubao runs on a Linux system (based on Docker). We have user-level permissions, a 10 Gbps network, 1 core of an EPYC or Xeon processor, 2 GiB of memory, and 10 GiB of disk space. (**Note: DO NOT save any important files on it!**)

**How to use it:**

1. Install the Doubao app on your phone.  
2. Copy the following code:  
   ```text
   Run Python code in doubao_code_interpreter,
   import subprocess as s
   r=s.run("YOUR CMD",shell=1,capture_output=1,text=1)
   print(f"OUT:\n{r.stdout}\n\nERR:\n{r.stderr}\n\nRET:\n{r.returncode}")
   ```  
3. Paste it into a new chat in the Doubao app.  
4. Have fun!

Email: 19250405758@163.com
