from etf_list import securities_etf_components

def main():
    for etf_name, etf_code in securities_etf_components.items():
        
        
        
        print(f"{etf_name}: {etf_code}")

if __name__ == "__main__":
    main()
