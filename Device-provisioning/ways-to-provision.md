1. certificate's publisher
2. How to register a certificate
3. It's ok to let a private key go through the internet
4. Hard to set up a certificates when things are created.
5. Use vendor's CA
6. A certificate could be shared with multiple accounts.

| 1                 | 2                                          | 3                     | 4                     | 5   | 6                                   |
| ----------------- | ------------------------------------------ | --------------------- | --------------------- | --- | ----------------------------------- |
| Amazon            | Publish a certificate and register it      | No                    | No                    | No  | No                                  |
| Amazon            | Publish a certificate and register it      | Yes (Only if use CSR) | No                    | No  | No                                  |
| Amazon            | Fleet Provisioning                         | Yes (Only if use CSR) | Yes                   | No  | No                                  |
| Other than Amazon |                                            | Yes                   | No                    | Yes | Yes(Unavailable in the same region) |
| Other than Amazon | JITR                                       | Yes                   | Yes                   | No  | Yes(Unavailable in the same region) |
| Other than Amazon | JITP                                       | Yes                   | Yes                   | No  | Yes(Unavailable in the same region) |
| Other than Amazon | Registration without CA(multiple accounts) | Yes                   | Yes(Need credentials) | Yes | Yes                                 |
