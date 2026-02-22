## ⚠️ WARNING

**THIS WILL DELETE ALL DATA FROM YOUR PS5**,

Continue **if you accept this risk**.

---

## Y2JB Installation

### Requirements

* USB stick **32 GB or larger**
* USB formatted as **exFAT (recommended)** or **FAT32**
* Internet access (DNS will be customized later)

---

### Step 1: Download Y2JB Backup

Download the `Y2JB_backup_VerNumber.7z` file from the latest release:

**[Y2JB Releases – Latest](https://github.com/Gezine/Y2JB/releases/latest)**

---

### Step 2: Create a PS5 Backup

1. Plug in a USB stick to your computer
2. Format your USB stick as **exFAT**.
3. Plug the USB stick into your PS5.
4. Navigate to:

```
Settings > System > Back Up and Restore > Back Up Your PS5
```

4. **De‑select everything**
   (Unless your USB is large enough and you want to backup installed games.)
5. Select **Next**, then **Back Up**.
6. Wait for the backup process to complete.

---

### Step 3: Inject Y2JB Backup

1. Extract `Y2JB_backup_VerNumber.7z` **on your computer** (do **not** extract to the USB).
2. You should see a `PS5` folder.
3. Navigate to:

```
PS5 > EXPORT > BACKUP
```

4. Copy the folder with alot of numbers in its name into:

```
USB/PS5/EXPORT/BACKUP
```

5. Safely eject the USB stick from your computer.

---

### Step 4: Restore the Modified Backup

1. Plug the USB stick back into your PS5.
2. Navigate to:

```
Settings > System > Back Up and Restore > Restore Your PS5
```

3. Select the backup labeled:

```
Y2JB VerNumber by Gezine
```

4. Select **Restore**, then **Yes**.

⚠️ **THIS WILL DELETE ALL INSTALLED APPS, GAMES, MEDIA, AND RESET SYSTEM SETTINGS**

---

### Step 5: Network Setup (Custom DNS)

1. Log in as **User1**.
2. Navigate to:

```
Settings > Network > Settings > Set Up Internet Connection
```

3. Scroll to the bottom and select **Set Up Manually**.
4. Choose:
   * **Use Wi‑Fi**
   * **Enter Manually**
5. Enter:
   * SSID (Wi-Fi Name)
   * Security: WPA‑Personal / WPA2‑Personal / WPA3‑Personal
   * Password
6. Leave all settings default **except DNS Settings**:

   * **Primary DNS:** `127.0.0.2`
7. Confirm and continue.

You will see a message telling you that the internet connection was unsuccessful — **this is expected**. Ignore it.

---

### Step 6: Launch Entry Point

1. Open the **YouTube app** from the **Media** section.

---

## Notes
To run code use 
```
Tools/Y2JB/payload_sender.py
```
**ALL** Code must be .js format!

## Firmware Notes

* **Firmware < 10.01** → Full jailbreak possible
* **Firmware ≥ 10.01** → Userland code execution only
