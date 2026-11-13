# Research: BLE ring with iPhone, Android and Mac (notifications and control)

Date read: 2026-11-11, between 09:07 and 09:14 UTC, unless a line says otherwise.

Tags:
- [F] = page opened and read. Raw HTML was saved with curl, and each quote was checked with grep in the saved text.
- [F-tool] = page read through the WebFetch summary tool. The quote is the tool's text, not checked against raw HTML.
- [S] = search result text only. Page not opened.

Raw copies (session scratchpad, not in the repo): <scratch>/ (files named in brackets below, for example ancs-spec.txt).

"ADG" = Apple Accessory Design Guidelines for Apple Devices, PDF https://developer.apple.com/accessories/Accessory-Design-Guidelines.pdf, "Release R32 Update 1" (adg.txt:4), page footers dated 2026-10-30. Cited as ADG page and adg.txt line.

## 1. iPhone notifications: ANCS

- Purpose [F-tool]. Source: https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Introduction/Introduction.html. Quote: "The purpose of the Apple Notification Center Service (ANCS) is to give Bluetooth accessories (that connect to iOS devices through a Bluetooth low-energy link) a simple and convenient way to access many kinds of notifications that are generated on iOS devices."
- Notification Source [F] (Specification page, ancs-spec.txt:102). Quote: "The Notification Source characteristic is the characteristic upon which an NC is informed of: The arrival of a new iOS notification on the NP; The modification of an iOS notification on the NP; The removal of an iOS notification on the NP". Source URL: https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Specification/Specification.html
- Categories [F] (ancs-appendix.txt:99). Quote: "CategoryIDOther = 0, CategoryIDIncomingCall = 1, CategoryIDMissedCall = 2, CategoryIDVoicemail = 3, CategoryIDSocial = 4, CategoryIDSchedule = 5, CategoryIDEmail = 6, CategoryIDNews = 7, CategoryIDHealthAndFitness = 8, CategoryIDBusinessAndFinance = 9, CategoryIDLocation = 10, CategoryIDEntertainment = 11, Reserved CategoryID values = 12–255". Source: https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Appendix/Appendix.html
- Fields, title, message, app, actions [F] (ancs-appendix.txt:116-119). Quote: "NotificationAttributeIDAppIdentifier = 0, NotificationAttributeIDTitle = 1, (Needs to be followed by a 2-bytes max length parameter) NotificationAttributeIDSubtitle = 2, (Needs to be followed by a 2-bytes max length parameter) NotificationAttributeIDMessage = 3, (Needs to be followed by a 2-bytes max length parameter) NotificationAttributeIDMessageSize = 4, NotificationAttributeIDDate = 5, NotificationAttributeIDPositiveActionLabel = 6, NotificationAttributeIDNegativeActionLabel = 7". Action IDs (ancs-appendix.txt:124): "ActionIDPositive = 0, ActionIDNegative = 1". Action flags (ancs-appendix.txt:105, 107): "EventFlagPositiveAction = (1 << 3)" and "EventFlagNegativeAction = (1 << 4)".
- Actions version (ancs-spec.txt:129). Quote: "Starting with iOS 8.0, the NP can inform the NC of potential actions that are associated with iOS notifications. On the user’s behalf, the NC can then request the NP to perform an action associated with a specific iOS notification."
- Category and UID (ancs-spec.txt:102). Quote: "CategoryID: A numerical value providing a category in which the iOS notification can be classified." and "NotificationUID: A 32-bit numerical value that is the unique identifier (UID) for the iOS notification. This value can be used as a handle in commands sent to the Control Point characteristic to interact with the iOS notification."
- Requirements, authorization [F] (ancs-spec.txt:101). Quote: "All these characteristics require authorization for access."
- Requirements, subscribe and Service Changed [F] (ancs-spec.txt:99). Quote: "As a result, the NC should look for and subscribe to the Service Changed characteristic of the GATT service in order to monitor for the potential publishing and unpublishing of the ANCS at any time."
- GATT client role: the spec never uses the words "GATT client" or "central". The client role is implied by subscribing to and writing to the iOS device's characteristics (ancs-spec.txt:102, "GATT notifications may be delivered as soon as the NC subscribes to the Notification Source characteristic."). Introduction [F-tool]: "An accessory acting as a GATT client is free to access and use other services provided by the iOS device while using the ANCS."
- Advertising and UUID [F] (adg.txt:16872). ADG: "ANCS uses 7905F431-B5CE-4E99-A40F-4B1E122D00D0 as its UUID." Service availability (adg.txt:16870): "Devices make Battery Service, Current Time Service, and Apple Notification Center Service (ANCS) available to an accessory."
- Service solicitation in advertising: not stated for ANCS. Searched ancs-spec.txt for "advertis" and "solicit": no line about advertising the ANCS (the only "solicit" hit is an unrelated Apple idea-submission line). ADG 57.4 (adg.txt, section 57.4 on the advertising data) says only the primary services should be advertised, without naming ANCS.
- Bonding, encryption, pairing: not stated in the ANCS spec. Searched ancs-spec.txt for bond, encrypt, pair: the only security term is "authorization" (line 101). ADG 57.9 [F] (adg.txt:16770): "The accessory should not require special permissions, such as pairing, authentication, or encryption, to discover services and characteristics." ADG 57.10 [F] (adg.txt:16800-16802): "Pairing may require user authorization depending on the device. Once an accessory is paired with a device, the accessory shall retain the distributed keys of both central and peripheral for future use." and "If the pairing is no longer required, the accessory shall delete both sets of keys."
- iPhone app needed: not stated by the ANCS spec or the ADG. ADG 57.14 [F] (adg.txt:16895) says: "The following services are implemented internally by iOS and shall not be published by third-party iOS applications:", and the list that follows includes "Current Time Service" and "Apple Notification Center Service" (adg.txt:16895-16912).
- Limits [F]. Quote (ancs-spec.txt:99): "Only one instance of the ANCS may be present on an NP. Due to the nature of iOS, the ANCS is not guaranteed to always be present." Quote (ancs-spec.txt:146): "Because the ANCS is not designed to be a complete synchronization service, it does not keep track of state across sessions." Responses larger than the MTU are split into fragments (ancs-spec.txt:106). Byte order is little endian and strings are UTF-8 (ancs-spec.txt, Endianness and String Encoding, Introduction [F-tool]).
- Not stated: maximum number of notifications, maximum payload beyond MTU fragmentation, minimum iOS version except actions (iOS 8.0).

## 2. iPhone control: AMS and HID over GATT

AMS [F], ams-spec.txt. Source: https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleMediaService_Reference/Specification/Specification.html (the Introduction URL returned HTTP 404 on curl).
- Service UUID (ams-spec.txt:99): "The Apple Media Service is a primary Bluetooth 4.0 service whose service UUID is 89D3502B-0F36-433A-8EF4-C502AD55F8DC."
- Commands (ams-spec.txt:124): "The Remote Command characteristic is the characteristic by which an MR can send remote commands to affect the playback state of an MS, such as Play, Next Track, Increase Volume, etc."
- Track title and app name (ams-spec.txt:142): "For example, the MR can be informed about the title of the currently loaded track, or the name of the active media app."
- Player fields (ams-spec.txt:103): "Attributes for this entity include values such as its name, playback state, and playback volume."
- Success is not playback (ams-spec.txt:136): "A successful write implies that the command has been successfully forwarded to the active media player. It does not guarantee that the player actually acted on it."
- Subscribe first (ams-spec.txt:145): "In order to receive this data, an MR first needs to subscribe for GATT notifications on the Entity Update characteristic."
- Errors (ams-spec.txt:206): "Invalid State (0xA0): The MR has not properly set up the AMS, e.g. it wrote to the Entity Update or Entity Attribute characteristic without subscribing to GATT notifications for the Entity Update characteristic."
- Bonding, encryption, authorization: not stated. Searched ams-spec.txt for bond, encrypt, authoriz: 0 lines.
- Apple's AMS page is an archive page (search text [S] says dated 2014). The ADG does not mention AMS (adg.txt search for "AMS" and "Apple Media Service": no hit).

HID over GATT on iOS:
- ADG 54.1 [F] (adg.txt:15256-15260). Quote: "Accessories shall only send HID reports for changes in physical or virtual control surfaces declared in the corresponding HID descriptor." and "For example, the accessory shall never generate a "Play/Pause" event without the user pressing a dedicated "Play/Pause" button."
- ADG 57.13 [F] (adg.txt:16885). Quote: "When implementing HID over Bluetooth Low Energy, the accessory shall advertise the HID Service in the Advertising Data".
- ADG 57.14 [F] (adg.txt:16895). The HID Service is listed as "implemented internally by iOS and shall not be published by third-party iOS applications".
- Keyboard consumer usages [F] (adg.txt:4607-4618, ADG p.94, Table 14-3). Quote: "Keyboards may implement individual keys emitting the following HID Consumer page usages". The table lists Power, Menu, Snapshot, Display Brightness Increment and Decrement, Scan Next Track (0x00B5) and Scan Previous Track (0x00B6). Play/Pause and Volume usages are not in this table.
- Which HID device kinds iOS accepts, and from which iOS version: not stated in ADG or the Apple pages I read. [S] Apple developer forum (thread 773065, search text only) says an Apple DTS engineer wrote that the ADG has no HOGP-specific requirements and that iOS rejects a configuration it does not support, such as "Keyboard". Not verified.
- Pointer through AssistiveTouch [F]. Source: https://support.apple.com/en-bw/111775. Quote: "Learn how to connect a wired mouse, trackpad, or assistive Bluetooth device to control an onscreen pointer on your iPhone, iPad, or iPod touch." (at.txt:543). Quote: "If you're using a keyboard to control your pointer, you'll need to enable the Mouse Keys function." (at.txt:595). Path to Bluetooth devices (at.txt:555-557): "To connect a Bluetooth device:" then Settings > Accessibility > Touch > AssistiveTouch > Devices > Bluetooth Devices.
- Play, pause and volume through HID on iOS: not stated by Apple in the pages I read. [S] A Nordic forum thread (search text only) reports a camera grip whose volume-up consumer control key triggered the shutter on iOS 15 but not on iOS 16.
- Apple accessory design guidance on HID, the HID descriptor rules above (ADG 54.1, 14, 57.13, 57.14): found. The ADG says HID for spatial accessories uses HOGP: "Support Human Interface Device (HID) (page 320), see HID Over GATT Profile (HOGP) (page 157)." (adg.txt:6233).

## 3. iPhone time: Current Time Service

- [F] ADG 57.12.4 (adg.txt:16870-16872). Quote: "Devices make Battery Service, Current Time Service, and Apple Notification Center Service (ANCS) available to an accessory. The Current Time Service supports the current time and local time information characteristics. The service does not provide an "Adjust Reason" when the current time changes."
- So an accessory can read time from the iPhone through CTS, per the ADG. The ADG does not say which way time is set or how often it is updated. Not stated.
- Bluetooth SIG CTS page https://www.bluetooth.com/specifications/specs/current-time-service-1-1/ was read by curl, but the saved HTML has no spec text (the page is JavaScript-rendered). Not found on that page.

## 4. Android notifications

Standard BLE notification service on Android (ANCS equivalent): not found. Pages tried: AOSP Bluetooth services https://source.android.com/docs/core/connect/bluetooth/services?hl=en (profile table, r2.txt:2145-2146 lists "MAP / Message Access Profile for SMS", a classic profile, with no BLE notification service in the rows I read). Android BLE background page and NotificationListenerService page did not name one.

NotificationListenerService [F] (and1.txt:26643-26670). Source: https://developer.android.com/reference/android/service/notification/NotificationListenerService
- Quote (26643): "A service that receives calls from the system when new notifications are posted or removed, or their ranking changed."
- Permission (26646): "To extend this class, you must declare the service in your manifest file with the Manifest.permission.BIND_NOTIFICATION_LISTENER_SERVICE permission"
- Wait for connect (26664): "The service should wait for the onListenerConnected() event before performing any operations."
- Limits (26668): "Notification listeners cannot get notification access or be bound by the system on low-RAM devices running Android Q (and below)." Also (26670): "The system also ignores notification listeners running in a work profile."
- User grant [F] (r4.txt:2018). Source: https://source.android.com/docs/automotive/hmi/notifications/notification-access. Quote: "access to notifications can be turned off by users in the Notification Access settings in the Settings app." This page is the Automotive policy page. It describes the privileged ACCESS_NOTIFICATIONS permission (r4.txt:2013), which a third-party app does not get, so it is not a general Android rule. Third-party user grant is described only through the Settings text above.

CompanionDeviceManager [F] (and3.txt). Source: https://developer.android.com/reference/android/companion/CompanionDeviceManager
- Notification access (and3.txt:27539-27540): "Your app must have an association with a device before calling this API." and "Side-loaded apps must allow restricted settings before requesting notification access."
- Presence (and3.txt:27569-27571): "Register to receive callbacks whenever the associated device's presence changes." and "BLE range changes (in/out)"; also "Bluetooth connection status changes (connected/disconnected)". Caller must implement CompanionDeviceService (and3.txt, same section). The API is marked "Added in API level 36".

Background BLE [F] (and5.txt:3329-3362). Source: https://developer.android.com/develop/connectivity/bluetooth/ble/background
- Quote (3329): "There is no restriction on connecting to a device while the app is in the background, although the connection is closed if your process is killed."
- Quote (3356): "Start a foreground service with the connectedDevice type."
- Quote (3354): "However, foreground service launch restrictions" with "apply starting in Android 12" (same passage).

Google Play policy [F] (play.txt). Source: https://support.google.com/googleplay/android-developer/answer/16559646?hl=en (title "Permissions and APIs that Access Sensitive Information"). Quote (play.txt:364, cut at the line end in the saved copy): "To safeguard user privacy, Google Play defines restricted permissions, subjecting them to additional requirements". The page does not name notification listener or BIND_NOTIFICATION_LISTENER_SERVICE (search of play.txt: 0 hits). So: not found on this page. Other Play policy pages were not opened.

## 5. Android control: HOGP

- AOSP profile table [F] (r2.txt:2238-2239, 2299). Source: https://source.android.com/docs/core/connect/bluetooth/services?hl=en. Rows: "HOGP 1.0 | HID over GATT" and "LE peripheral mode". The version columns for Android releases were not parsed, so the Android version where HOGP first works is not found.
- Android HID device API [F] (r3.txt:26631). Source: https://developer.android.com/reference/android/bluetooth/BluetoothHidDevice. Quote: "Provides the public APIs to control the Bluetooth HID Device profile." The class is marked "Added in API level 28" (r3.txt:26608, nearest API-level line before the class heading at r3.txt:26624). This is the classic HID device profile API. The page did not show a BLE or GATT peripheral API in the lines I checked.
- Google limits for HOGP peripheral use: not found. Pages tried: developer.android.com HID guide https://developer.android.com/develop/connectivity/bluetooth/hid (HTTP 404); BLE overview https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview (no HID text read).
- [S] Search text only: a HSC blog describes an Android phone acting as a classic HID mouse and keyboard, with the note that the stock stack supports the HID host role only. A GitHub project describes an Android app emulating a BLE HID peripheral. Neither is an official source.

## 6. Mac notifications

- ANCS on macOS: not stated by Apple in the ADG. ADG 57.12.4 (adg.txt:16870) says "Devices make ... available to an accessory" with no Mac wording. ADG 57.7 (adg.txt:16755) says: "Devices and Mac computers operating as the Central will negotiate optimal data packet lengths". This shows the Mac is a Central in the ADG text, not that it offers ANCS.
- macOS notifications to a Bluetooth accessory by any standard service: not found in pages tried (ADG; Mac Help page below).
- API for a Mac app to read other apps' notifications: not found. I did not get an Apple page that answers it in the time available. Not stated by Apple in pages I read.
- Mac app CoreBluetooth in background, central role [F] (cb-bg.txt:18). Source: the only Apple background page I opened is the iOS archive page https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html. Quote: "Core Bluetooth background execution modes to allow your app to be woken up from a suspended state to process certain Bluetooth-related events." Quote: "cannot scan for and discover advertising peripherals while in the background or while suspended." This is iOS. macOS behaviour: not stated by Apple in this page. Current Apple developer page /documentation/corebluetooth/using-core-bluetooth-in-the-background returned HTTP 404 on curl.
- [S] Search text only: a Core Bluetooth reference note says background modes are not supported in iPad apps running on Mac. Not verified.

## 7. Mac control: BLE HID

- [F] Mac Help "Connect a Bluetooth device with your Mac" (mac-bt.txt:5275). Source: https://support.apple.com/guide/mac-help/blth1004. Quote: "Use Bluetooth ® to connect your Mac to a keyboard, mouse, trackpad, headphones, or speakers." This page is generic. It does not say whether a third-party BLE HID keyboard, consumer control or pointer is supported, or from which macOS version.
- Keyboard and trackpad help page exists (mac-bt.txt:1203, "Keyboard and trackpad"). Not opened.
- Apple statements on BLE HID keyboards, consumer control keys or pointers on macOS: not found in pages tried (ADG; Mac Help blth1004).

## 8. More than one device: bonds and connections

- Bluetooth Core Specification, Security Manager page [F] (sm.txt). Source: https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host/security-manager-specification.html. Quote (sm.txt:185): "The Bonding_Flags field is a 2-bit field that indicates the type of bonding being requested by the initiating device". Search of sm.txt for "more than one", "several", "multiple" found no statement about bonding with several devices (only "multiple bit fields" at sm.txt:87). Not found on this page. Whether a peripheral can be bonded to several hosts is not found in the Core spec pages I read.
- HOGP 1.0 spec: the bluetooth.com HOGP page (m4) saved HTML has no spec text. Not found. 
- Apple ADG on bonds per accessory [F] (adg.txt:16800-16802, see section 1). The accessory "shall retain the distributed keys of both central and peripheral for future use." This is per central pairing. Multi-host behaviour is not stated.
- Apple ADG on reconnection [F] (adg.txt:16878). Quote: "The device will maintain a connection to an accessory as long as it is paired and uses one of the available services." This is the device (iPhone or Mac) side. It does not say reconnection happens for HID.
- [S] Search text only, not verified: a BlueZ mailing-list thread cites HOGP 1.0 Section 6.1 for a bonding requirement (lore.kernel.org). A Punch Through article says iOS and Android reconnect the same for bonded and unbonded devices. An Apple developer forum thread (695730) reports iOS not reconnecting automatically to a bonded BLE mouse.
- Connected to more than one host at once: not found.

## 9. Rules that bind a product

- MFi [F] (adg.txt:973-974). Quote: "Use of some features requires accessory developers to be a member of the program and to integrate specific MFi hardware into the accessory." Source: ADG section 3.8 (ADG p.22). Also (adg.txt:13762) for Siri over other transports: "To support Siri using other transports and protocols, the accessory developer shall be a member of the Apple MFi Program (page 22)."
- Is MFi needed for ANCS, AMS or HID: not stated in the ADG. Searched adg.txt for MFi and "Made for": 10 lines, none names ANCS, AMS, HID or BLE. ANCS appears only at adg.txt:16870 and 16872, with no MFi wording.
- SIG profile names [F]: "HID over GATT Profile (HOGP)" (adg.txt:8219, section 19.4.5.3) and "HOGP 1.0 | HID over GATT" (r2.txt:2238-2239).
- Apple ANCS UUID [F]: 7905F431-B5CE-4E99-A40F-4B1E122D00D0 (adg.txt:16872).
- Battery Service: ADG p.242, section 33, "Bluetooth Low Energy Battery Service" (ADG table of contents, adg.txt:379). Battery Service UUID 0x180F, HID service UUID 0x1812 and CTS UUID 0x1805: [S] search text only (Zephyr, Nordic and Wireshark sources). The SIG assigned numbers page https://www.bluetooth.com/specifications/assigned-numbers/ was saved, but the table is not in the static HTML. Not verified against the SIG page.
- Apple accessory programme rules that apply to ANCS, AMS or HID: the ADG rules above (54.1, 57.x). Apple's MFi programme page https://mfi.apple.com was not opened (it may need login). Not checked.

## Not found (summary)
- Standard BLE notification service on Android: pages tried in section 4.
- macOS ANCS or any macOS notification access API for accessories: pages tried in section 6.
- iOS version from which HID keyboard, consumer keys or pointer work: pages tried in section 2 (ADG, AssistiveTouch page).
- Google's stated limits for HOGP peripherals: pages tried in section 5.
- Multi-bond and multi-connection rules in the Core spec and HOGP spec: pages tried in section 8.
- Play policy text on notification listener access: play.txt, section 4.

RESULT: done, all nine questions have sourced findings or a "not found" with pages tried, but macOS notification access, iOS HID version limits, and HOGP multi-bond rules remain unsourced.
