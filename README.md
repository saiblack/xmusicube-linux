# Xmusicube (Flatpak Version)

Xmusicube is a music player application packaged as a Flatpak for Linux.

## How to Build and Install

To build and install the application locally, ensure you have `flatpak` and `flatpak-builder` installed on your system.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd xmusicube
    ```

2.  **Build the Flatpak:**
    ```bash
    flatpak-builder --force-clean build-dir io.github.xmusicube.json
    ```

3.  **Install the Flatpak:**
    ```bash
    flatpak-builder --user --install --force-clean build-dir io.github.xmusicube.json
    ```

4.  **Run the application:**
    ```bash
    flatpak run io.github.xmusicube
    ```

## Development

The application source code is located in the `src/` directory, and data files (like the desktop entry and icons) are in the `data/` directory. The manifest file `io.github.xmusicube.json` defines the build process and dependencies.
# xmusicube-linux
