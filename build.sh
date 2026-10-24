#!/bin/sh
set -eu
curl --fail --silent --show-error --location https://dot.net/v1/dotnet-install.sh > dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh --channel 10.0 --quality GA --install-dir ./dotnet
./dotnet/dotnet --version
./dotnet/dotnet publish HEIC2JPG/HEIC2JPG.csproj -c Release -o output
