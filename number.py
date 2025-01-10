import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import time
from colorama import Fore, Style, init
import requests
import json
import os

# Initialize colorama
init()

def print_banner():
    banner = f"""
{Fore.RED}╔═══════════════════════════════════════════════════════════════╗
║             PHONE NUMBER OSINT RECONNAISSANCE TOOL              ║
║                Created by Filius a.k.a .Sp4xx                   ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}"""
    print(banner)

def animate_loading():
    chars = "/—\\|"
    for char in chars:
        print(f'\r{Fore.CYAN}[{char}] Analyzing...{Style.RESET_ALL}', end='')
        time.sleep(0.1)

def get_additional_info(country_code):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/alpha/{country_code}")
        if response.status_code == 200:
            data = response.json()[0]
            return {
                "capital": data.get("capital", ["Unknown"])[0],
                "region": data.get("region", "Unknown"),
                "population": data.get("population", "Unknown"),
                "currencies": ", ".join(data.get("currencies", {}).keys()),
                "languages": ", ".join(data.get("languages", {}).values()),
                "timezones": ", ".join(data.get("timezones", [])),
                "area": data.get("area", "Unknown"),
                "borders": ", ".join(data.get("borders", [])),
                "flag": data.get("flag", "Unknown"),
                "subregion": data.get("subregion", "Unknown"),
                "continents": ", ".join(data.get("continents", []))
            }
    except:
        return None
    return None

def get_number_type(parsed_number):
    number_type = phonenumbers.number_type(parsed_number)
    types = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
    }
    return types.get(number_type, "Unknown")

def phone_number_info(number, mass_scan=False):
    try:
        if not mass_scan:
            print(f"\n{Fore.YELLOW}[+] Initiating reconnaissance on {number}{Style.RESET_ALL}\n")
            
            for _ in range(10):
                animate_loading()
            print("\n")

        # Parse the phone number
        parsed_number = phonenumbers.parse(number)
        
        # Check if number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            return f"{Fore.RED}[!] Invalid phone number detected: {number}{Style.RESET_ALL}"
            
        # Get basic info
        location = geocoder.description_for_number(parsed_number, "en")
        service_provider = carrier.name_for_number(parsed_number, "en")
        time_zones = timezone.time_zones_for_number(parsed_number)
        international_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        country_code = phonenumbers.region_code_for_number(parsed_number)
        number_type = get_number_type(parsed_number)
        
        # Get additional country information
        country_info = get_additional_info(country_code)
        
        # Build detailed result
        result = f"""
{Fore.GREEN}[+] ANALYSIS FOR {international_format}{Style.RESET_ALL}
{Fore.CYAN}═══════════════════════════════════════════════════════════════

[*] BASIC INFORMATION
{Fore.WHITE}├─ International Format : {international_format}
├─ National Format    : {national_format}
├─ Country Code      : +{parsed_number.country_code}
├─ National Number   : {parsed_number.national_number}
├─ Number Type       : {number_type}
├─ Valid Number      : Yes
└─ Raw Input         : {number}{Style.RESET_ALL}

{Fore.CYAN}[*] GEOLOCATION INFORMATION
{Fore.WHITE}├─ Country           : {location}
├─ Time Zones        : {', '.join(time_zones)}
└─ Service Provider  : {service_provider}{Style.RESET_ALL}
"""

        if country_info:
            result += f"""
{Fore.CYAN}[*] ADDITIONAL COUNTRY INFORMATION
{Fore.WHITE}├─ Capital City      : {country_info['capital']}
├─ Region            : {country_info['region']}
├─ Subregion        : {country_info['subregion']}
├─ Continents       : {country_info['continents']}
├─ Population       : {country_info['population']:,}
├─ Area             : {country_info['area']:,} sq km
├─ Currencies       : {country_info['currencies']}
├─ Languages        : {country_info['languages']}
├─ Timezones        : {country_info['timezones']}
├─ Bordering Countries: {country_info['borders']}
└─ Flag             : {country_info['flag']}{Style.RESET_ALL}
"""

        if not mass_scan:
            result += f"\n{Fore.GREEN}[✓] Reconnaissance completed successfully{Style.RESET_ALL}"
        return result
        
    except Exception as e:
        return f"{Fore.RED}[!] Error analyzing {number}: {str(e)}{Style.RESET_ALL}"

def mass_scan_from_file(filename):
    try:
        if not os.path.exists(filename):
            return f"{Fore.RED}[!] File not found: {filename}{Style.RESET_ALL}"
            
        with open(filename, 'r') as file:
            numbers = file.readlines()
        
        numbers = [num.strip() for num in numbers if num.strip()]
        
        print(f"\n{Fore.YELLOW}[+] Starting mass scan of {len(numbers)} numbers{Style.RESET_ALL}")
        
        results = []
        for i, number in enumerate(numbers, 1):
            print(f"\n{Fore.CYAN}[*] Processing number {i}/{len(numbers)}{Style.RESET_ALL}")
            result = phone_number_info(number, mass_scan=True)
            results.append(result)
            
        # Save results to file
        output_file = f"osint_results_{int(time.time())}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(results))
            
        return f"\n{Fore.GREEN}[✓] Mass scan completed! Results saved to: {output_file}{Style.RESET_ALL}"
        
    except Exception as e:
        return f"{Fore.RED}[!] Error during mass scan: {str(e)}{Style.RESET_ALL}"

def main():
    try:
        print_banner()
        print(f"\n{Fore.YELLOW}[?] Select scan mode:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[1] Single number scan")
        print(f"[2] Mass scan from file{Style.RESET_ALL}")
        
        mode = input(f"\n{Fore.YELLOW}[?] Enter your choice (1/2): {Style.RESET_ALL}")
        
        if mode == "1":
            number = input(f"\n{Fore.YELLOW}[?] Enter phone number with country code (e.g. +6281234567890): {Style.RESET_ALL}")
            print(phone_number_info(number))
        elif mode == "2":
            filename = input(f"\n{Fore.YELLOW}[?] Enter the path to your text file containing phone numbers: {Style.RESET_ALL}")
            print(mass_scan_from_file(filename))
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] An unexpected error occurred: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

