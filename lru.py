import os
import platform

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

    print("LOPEZ, Amir Jo-hanz B.")
    print("ML-M4: ACT4 - Least Recently Used\n")

def clear_lines(n=1):
    for _ in range(n):
        print("\033[A\033[K", end="")

def get_valid_int(prompt, max_val=None):
    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                raise ValueError
            if max_val and val > max_val:
                print(f"{Colors.RED}  [!] Error: Maximum value is {max_val}.{Colors.RESET}")
                input("  Press Enter to retry...")
                clear_lines(3)
                continue
            return val
        except ValueError:
            print(f"{Colors.RED}  [!] Error: Positive integer required.{Colors.RESET}")
            input("  Press Enter to retry...")
            clear_lines(3)

def print_transposed_table(table_data, current_step, num_frames, dealloc_info=None): 
    # 1. Request Row (Header)
    req_row = f"| {' ':<6} |"
    for i in range(current_step):
        req_row += f" {table_data[i]['request']:^3} |"
        
    separator = "-" * len(req_row)
    
    print(f"{Colors.YELLOW}--- LRU PAGE REPLACEMENT TABLE ---{Colors.RESET}")
    print(separator)
    print(req_row)
    print(separator)
    
    # 2. Frame Rows (Y-axis)
    for f in range(num_frames):
        frame_row = f"| {f'Frame{f+1}':<6} |"
        for i in range(current_step):
            data = table_data[i]
            is_active_step = (i == current_step - 1)
            
            if is_active_step and dealloc_info and dealloc_info['step_idx'] == i and dealloc_info['frame_idx'] == f:
                item = f"{Colors.RED}{dealloc_info['old_page']:^3}{Colors.RESET}"
            else:
                val = data['frames'][f]
                prev_val = table_data[i-1]['frames'][f] if i > 0 else "---"
                
                if val != "---" and val != prev_val:
                    if is_active_step and not dealloc_info:
                        item = f"{Colors.GREEN}{val:^3}{Colors.RESET}"
                    else:
                        item = f"{val:^3}"
                else:
                    item = f"{val:^3}"
                    
            frame_row += f" {item} |"
        print(frame_row)
        
    print(separator)
    
    # 3. Page Fault Row
    fault_row = f"| {'PF':<6} |"
    for i in range(current_step):
        fault = table_data[i]['fault']
        f_str = f"{Colors.RED}*{Colors.RESET}" if fault else f"{Colors.GREEN} {Colors.RESET}"
        fault_row += f"  {f_str}  |"
    print(fault_row)
    print(separator)

def main():
    clear_screen()

    # --- 1. Inputs & Validation ---
    num_frames = get_valid_int("Enter No. of Frames: ")
    num_pages = get_valid_int("Enter No. of Pages: ", max_val=26)
    
    page_list = [chr(65 + i) for i in range(num_pages)]
    print(f"\n{Colors.GREEN}>> Page List generated: {', '.join(page_list)}{Colors.RESET}\n")
    
    num_reqs = get_valid_int("Enter No. of Requested Pages: ")
    requested_pages = []
    
    print("\nEnter The Requested Pages: ")
    for i in range(num_reqs):
        while True:
            req = input(f"  Request {i+1}: ").strip().upper()
            if req in page_list:
                requested_pages.append(req)
                break
            else:
                print(f"{Colors.RED}  [!] Invalid. Page must be one of: {', '.join(page_list)}{Colors.RESET}")
                input("  Press Enter to retry...")
                clear_lines(3)

    # --- 2. LRU Pre-computation Logic ---
    frames = ["---"] * num_frames
    lru_queue = [] 
    page_faults = 0
    page_hits = 0
    table_data = []

    for req in requested_pages:
        fault_occurred = False
        replaced_page = None
        replaced_frame_idx = None
        action_msg = ""
        
        if req in frames:
            # PAGE HIT
            page_hits += 1
            fault_occurred = False
            lru_queue.remove(req)
            lru_queue.append(req)
            action_msg = f"PAGE HIT: Page '{req}' is already in memory."
        else:
            # PAGE FAULT
            page_faults += 1
            fault_occurred = True
            
            if "---" in frames:
                # Still have empty frames (No replacement needed)
                empty_idx = frames.index("---")
                frames[empty_idx] = req
                lru_queue.append(req)
                action_msg = f"PAGE FAULT: Allocated '{req}' to Frame {empty_idx + 1}."
            else:
                # Frames full, need LRU replacement
                lru_page = lru_queue.pop(0) 
                replaced_frame_idx = frames.index(lru_page)
                replaced_page = lru_page
                
                frames[replaced_frame_idx] = req 
                lru_queue.append(req)     
                
                action_msg = f"PAGE FAULT: Allocated '{req}' to Frame {replaced_frame_idx + 1}."

        table_data.append({
            'request': req,
            'frames': frames.copy(),
            'fault': fault_occurred,
            'replaced_page': replaced_page,
            'replaced_frame_idx': replaced_frame_idx,
            'msg': action_msg
        })

    # --- 3. Step-by-Step Interactive Display ---
    input("\nConfiguration Complete. Press Enter to start the simulation...")
    
    for step in range(1, num_reqs + 1):
        data = table_data[step - 1]
        
        # PHASE A: DEALLOCATION (If replacement occurred)
        if data['replaced_page']:
            clear_screen()
            print(f"{Colors.GREEN}Page List: {', '.join(page_list)}{Colors.RESET}\n")
            
            dealloc_info = {
                'step_idx': step - 1, 
                'frame_idx': data['replaced_frame_idx'], 
                'old_page': data['replaced_page']
            }
            print_transposed_table(table_data, step, num_frames, dealloc_info)
            
            print(f"\n{Colors.RED}>> PAGE FAULT: Deallocating LRU page '{data['replaced_page']}' from Frame {data['replaced_frame_idx'] + 1}...{Colors.RESET}")
            input("   Press Enter to clear memory and allocate new page...")

        # PHASE B: ALLOCATION / HIT
        clear_screen()
        print(f"{Colors.GREEN}Page List: {', '.join(page_list)}{Colors.RESET}\n")
        
        print_transposed_table(table_data, step, num_frames)
        print(f"\n{Colors.GREEN}>> Action:{Colors.RESET} {data['msg']}")
        
        if step < num_reqs:
            input("   Press Enter to process next Request...")
        else:
            input("\n   Press Enter to view final summary...")

    # --- 4. Conclusion ---
    clear_screen()
    print(f"{Colors.GREEN}Page List: {', '.join(page_list)}{Colors.RESET}\n")
    print_transposed_table(table_data, num_reqs, num_frames)
    
    print(f"\n{Colors.YELLOW}=== SUMMARY ==={Colors.RESET}")
    print(f"Total Page Requests : {num_reqs}")
    print(f"Total Page Faults   : {Colors.RED}{page_faults}{Colors.RESET}")
    print(f"Total Page Hits     : {Colors.GREEN}{page_hits}{Colors.RESET}")
    print("-" * 40)
    
    input("\nPress Enter to exit.")

if __name__ == "__main__":
    main()