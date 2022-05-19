# vyos-tailscale-integrated

Builds on the work from [DMarby/vyos-tailscale](https://github.com/DMarby/vyos-tailscale) and integrates tailscale as a configurable service in vyos

## Usage

Building an ISO requires docker to be accessible from the user calling build.py

```bash
./build.py
```

The resulting iso will be available under `vendor/vyos-build/build/vyos-1.3-equuleus-tailscale-amd64.iso`

## Roadmap

- [ ] Add support for selecting a vyos-1x commit hash to build from
- [ ] Add support for building the `current` (1.4) branch of vyos
- [ ] Add support for configuring the tailscale listening port from the vyos cli
- [X] Add the tailscale interface to vyos to make autocomplete easier for things like firewall configuration, as well as having it show up under `show interfaces`
- [ ] Properly handle the case where we are bringing up tailscale for the first time, instead of just catching TimeoutExpired
