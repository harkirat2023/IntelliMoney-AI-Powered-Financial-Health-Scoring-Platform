from dataclasses import dataclass


@dataclass
class AliasEntry:
    pattern: str
    alias_type: str  # "exact", "contains", "regex"
    priority: int = 0


@dataclass
class MerchantEntry:
    display_name: str
    category: str
    aliases: list[AliasEntry]


MERCHANTS: dict[str, MerchantEntry] = {
    "swiggy": MerchantEntry("Swiggy", "Food", [
        AliasEntry("swiggy", "contains", 10),
        AliasEntry(r"swiggy.*ref\d+", "regex", 5),
    ]),
    "zomato": MerchantEntry("Zomato", "Food", [
        AliasEntry("zomato", "contains", 10),
        AliasEntry(r"zomato.*ref\d+", "regex", 5),
    ]),
    "uber": MerchantEntry("Uber", "Transport", [
        AliasEntry("uber", "contains", 10),
        AliasEntry(r"uber\s*india", "regex", 5),
    ]),
    "ola": MerchantEntry("Ola", "Transport", [
        AliasEntry("ola", "contains", 10),
    ]),
    "amazon": MerchantEntry("Amazon", "Shopping", [
        AliasEntry("amazon", "contains", 10),
        AliasEntry(r"amz\*", "regex", 5),
    ]),
    "flipkart": MerchantEntry("Flipkart", "Shopping", [
        AliasEntry("flipkart", "contains", 10),
        AliasEntry(r"fk.*ref\d+", "regex", 5),
    ]),
    "netflix": MerchantEntry("Netflix", "Entertainment", [
        AliasEntry("netflix", "contains", 10),
        AliasEntry(r"netflix.*in", "regex", 5),
    ]),
    "spotify": MerchantEntry("Spotify", "Entertainment", [
        AliasEntry("spotify", "contains", 10),
    ]),
    "jio": MerchantEntry("Jio", "Bills", [
        AliasEntry("jio", "contains", 10),
        AliasEntry("reliance jio", "contains", 8),
    ]),
    "airtel": MerchantEntry("Airtel", "Bills", [
        AliasEntry("airtel", "contains", 10),
    ]),
    "dominos": MerchantEntry("Dominos", "Food", [
        AliasEntry("dominos", "contains", 10),
        AliasEntry("domino", "contains", 8),
    ]),
    "mcdonalds": MerchantEntry("McDonald's", "Food", [
        AliasEntry("mcdonald", "contains", 10),
        AliasEntry("mcd", "contains", 5),
    ]),
    "bigbasket": MerchantEntry("BigBasket", "Food", [
        AliasEntry("bigbasket", "contains", 10),
        AliasEntry(r"bb.*ref\d+", "regex", 5),
    ]),
    "zepto": MerchantEntry("Zepto", "Food", [
        AliasEntry("zepto", "contains", 10),
    ]),
    "blinkit": MerchantEntry("Blinkit", "Food", [
        AliasEntry("blinkit", "contains", 10),
    ]),
    "myntra": MerchantEntry("Myntra", "Shopping", [
        AliasEntry("myntra", "contains", 10),
    ]),
    "nykaa": MerchantEntry("Nykaa", "Shopping", [
        AliasEntry("nykaa", "contains", 10),
    ]),
    "bookmyshow": MerchantEntry("BookMyShow", "Entertainment", [
        AliasEntry("bookmyshow", "contains", 10),
        AliasEntry("bms", "contains", 5),
    ]),
    "1mg": MerchantEntry("1mg", "Health", [
        AliasEntry("1mg", "contains", 10),
    ]),
    "pharmeasy": MerchantEntry("PharmEasy", "Health", [
        AliasEntry("pharmeasy", "contains", 10),
    ]),
    "makemytrip": MerchantEntry("MakeMyTrip", "Travel", [
        AliasEntry("makemytrip", "contains", 10),
        AliasEntry("mmt", "contains", 5),
    ]),
    "goibibo": MerchantEntry("Goibibo", "Travel", [
        AliasEntry("goibibo", "contains", 10),
    ]),
    "irctc": MerchantEntry("IRCTC", "Travel", [
        AliasEntry("irctc", "contains", 10),
    ]),
    "google_one": MerchantEntry("Google One", "Bills", [
        AliasEntry("google one", "contains", 10),
    ]),
    "google_play": MerchantEntry("Google Play", "Entertainment", [
        AliasEntry("google play", "contains", 10),
        AliasEntry(r"g\.co", "regex", 5),
    ]),
    "apple": MerchantEntry("Apple", "Entertainment", [
        AliasEntry("apple", "contains", 10),
        AliasEntry("icloud", "contains", 8),
    ]),
    "prime_video": MerchantEntry("Amazon Prime", "Entertainment", [
        AliasEntry("prime video", "contains", 10),
        AliasEntry("prime amazon", "contains", 8),
    ]),
    "hotstar": MerchantEntry("Disney+ Hotstar", "Entertainment", [
        AliasEntry("hotstar", "contains", 10),
    ]),
    "zee5": MerchantEntry("ZEE5", "Entertainment", [
        AliasEntry("zee5", "contains", 10),
    ]),
    "tata_power": MerchantEntry("Tata Power", "Bills", [
        AliasEntry("tata power", "contains", 10),
    ]),
    "bses": MerchantEntry("BSES", "Bills", [
        AliasEntry("bses", "contains", 10),
    ]),
}


def get_merchant_by_key(key: str) -> MerchantEntry | None:
    return MERCHANTS.get(key.lower())


def get_all_merchants() -> dict[str, MerchantEntry]:
    return dict(MERCHANTS)
