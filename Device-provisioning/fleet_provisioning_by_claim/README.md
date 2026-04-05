# Fleet Provisioning Setup

## 1. Deploy Stack
```bash
./deploy.sh
```

Creates: Thing Type, Thing Group, Device Policy, Claim Policy, Provisioning Template, Lambda Hook, Claim Certificate

## 2. Get Claim Certificate
```bash
# Get outputs from stack
aws cloudformation describe-stacks \
  --stack-name fleet-stack \
  --query 'Stacks[0].Outputs'

# Note: Private key is NOT retrievable after creation
# For testing, create a new certificate:
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile claim.cert.pem \
  --private-key-outfile claim.private.key

# Attach to claim policy
aws iot attach-policy \
  --policy-name fleet-claim-policy \
  --target <CERT_ARN>
```

## 3. Run Client
```bash
cd iotdevice
# Edit client.py with endpoint and template name from outputs
python client.py
```

Device provisions automatically with permanent certificate
