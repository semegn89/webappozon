// Telegram WebApp types
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name?: string
            last_name?: string
            username?: string
            language_code?: string
          }
        }
        ready(): void
        expand(): void
        enableClosingConfirmation(): void
        close(): void
        showAlert(message: string): void
        showConfirm(message: string, callback: (confirmed: boolean) => void): void
        showPopup(params: any, callback: (buttonId: string) => void): void
        showScanQrPopup(params: any, callback: (text: string) => void): void
        closeScanQrPopup(): void
        readTextFromClipboard(callback: (text: string) => void): void
        requestWriteAccess(callback: (granted: boolean) => void): void
        requestContact(callback: (granted: boolean) => void): void
        openLink(url: string): void
        openTelegramLink(url: string): void
        openInvoice(url: string, callback: (status: string) => void): void
        sendData(data: string): void
        switchInlineQuery(query: string, choose_chat_types?: string[]): void
        version: string
        platform: string
        colorScheme: 'light' | 'dark'
        themeParams: any
        isExpanded: boolean
        viewportHeight: number
        viewportStableHeight: number
        headerColor: string
        backgroundColor: string
        isClosingConfirmationEnabled: boolean
        BackButton: {
          isVisible: boolean
          onClick(callback: () => void): void
          offClick(callback: () => void): void
          show(): void
          hide(): void
        }
        MainButton: {
          text: string
          color: string
          textColor: string
          isVisible: boolean
          isActive: boolean
          isProgressVisible: boolean
          setText(text: string): void
          onClick(callback: () => void): void
          offClick(callback: () => void): void
          show(): void
          hide(): void
          enable(): void
          disable(): void
          showProgress(leaveActive?: boolean): void
          hideProgress(): void
          setParams(params: any): void
        }
        HapticFeedback: {
          impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void
          notificationOccurred(type: 'error' | 'success' | 'warning'): void
          selectionChanged(): void
        }
        CloudStorage: {
          setItem(key: string, value: string, callback?: (error: string | null, result?: boolean) => void): void
          getItem(key: string, callback: (error: string | null, result?: string) => void): void
          getItems(keys: string[], callback: (error: string | null, result?: Record<string, string>) => void): void
          removeItem(key: string, callback?: (error: string | null, result?: boolean) => void): void
          removeItems(keys: string[], callback?: (error: string | null, result?: boolean) => void): void
          getKeys(callback: (error: string | null, result?: string[]) => void): void
        }
        BiometricManager: {
          isInited: boolean
          isBiometricAvailable: boolean
          biometricType: 'finger' | 'face' | 'unknown'
          isAccessRequested: boolean
          isAccessGranted: boolean
          isBiometricTokenSaved: boolean
          deviceId: string
          init(callback?: (error: string | null) => void): void
          requestAccess(params: any, callback: (error: string | null, result?: boolean) => void): void
          authenticate(params: any, callback: (error: string | null, result?: boolean) => void): void
          updateBiometricToken(token: string, callback?: (error: string | null, result?: boolean) => void): void
          openSettings(): void
        }
        onEvent(eventType: string, eventHandler: () => void): void
        offEvent(eventType: string, eventHandler: () => void): void
      }
    }
  }
}

export {}
