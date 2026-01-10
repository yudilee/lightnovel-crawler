import { getGradientForId } from '@/utils/gradients';
import { HeartFilled } from '@ant-design/icons';
import { Avatar, Button, Collapse, Flex, Modal, Space, Typography } from 'antd';
import { QRCodeSVG } from 'qrcode.react';
import { useState } from 'react';

interface CryptoInfo {
  name: string;
  icon: string;
  symbol: string;
  address: string;
}

// Cryptocurrency wallet addresses
const CRYPTO_WALLETS: CryptoInfo[] = [
  {
    name: 'Bitcoin',
    symbol: 'BTC',
    address: '1CVjbgQpXdtzsXMA6Rtrk5WvNiWuAQnLE',
    icon: '₿',
  },
  {
    name: 'Ethereum',
    symbol: 'ETH',
    address: '0xe925b6db4ee0bbc294a6a7d5b64a7c37e66199fa',
    icon: 'Ξ',
  },
  {
    name: 'Tether USD',
    symbol: 'USDT',
    address: '0xe925b6db4ee0bbc294a6a7d5b64a7c37e66199fa',
    icon: '💵',
  },
  {
    name: 'USD Coin',
    symbol: 'USDC',
    address: '6TRj4JD6ZWTnR5awC4x1o4RvU9fweFZd9QgL28Nk5oGC',
    icon: '💲',
  },
  {
    name: 'Solana',
    symbol: 'SOL',
    address: '6TRj4JD6ZWTnR5awC4x1o4RvU9fweFZd9QgL28Nk5oGC',
    icon: '◎',
  },
  {
    name: 'Litecoin',
    symbol: 'LTC',
    address: 'LYCWMBUyUYjhQFNibfAaJoBs2HqmgviWkb',
    icon: 'Ł',
  },
];

export const DonateButton = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        block
        type="primary"
        icon={<HeartFilled />}
        onClick={() => setOpen(true)}
      >
        Donate
      </Button>

      <Modal
        title={
          <Typography.Title level={4} style={{ margin: 0 }}>
            Donate with Cryptocurrency
          </Typography.Title>
        }
        open={open}
        onCancel={() => setOpen(false)}
        footer={null}
        width={600}
        destroyOnHidden
      >
        <Typography.Text
          type="secondary"
          style={{ fontSize: '14px', textAlign: 'center' }}
        >
          Your donations are greatly appreciated and help keep the project
          running.
        </Typography.Text>

        <Collapse
          accordion
          style={{ marginTop: '16px' }}
          defaultActiveKey={[CRYPTO_WALLETS[0].symbol]}
          items={CRYPTO_WALLETS.map((crypto) => ({
            key: crypto.symbol,
            label: (
              <Space>
                <Avatar
                  size={24}
                  icon={crypto.icon}
                  style={{
                    color: '#d9f134',
                    background: getGradientForId(crypto.name),
                  }}
                />
                <Typography.Text style={{ fontSize: '16px', fontWeight: 600 }}>
                  {crypto.name} ({crypto.symbol})
                </Typography.Text>
              </Space>
            ),
            children: <CryptoDonationTab crypto={crypto} />,
          }))}
        />

        <Space vertical style={{ marginTop: '16px', textAlign: 'center' }}>
          <Typography.Text type="success">
            Thank you for your support!
          </Typography.Text>
        </Space>
      </Modal>
    </>
  );
};

const CryptoDonationTab: React.FC<{ crypto: CryptoInfo }> = ({ crypto }) => {
  return (
    <Flex vertical align="center" justify="center">
      <div
        style={{
          padding: '20px',
          borderRadius: '8px',
          display: 'inline-block',
          backgroundColor: '#fff',
          marginBottom: '8px',
        }}
      >
        <QRCodeSVG
          value={crypto.address}
          size={256}
          level="M"
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      <Typography.Text
        copyable
        style={{
          fontFamily: 'monospace',
          fontSize: '16px',
          fontWeight: 600,
          letterSpacing: '0.07em',
          wordBreak: 'break-all',
          color: '#d9f134',
          textAlign: 'center',
          padding: '5px 10px',
          borderRadius: '8px',
          border: '1px solid #a9d134',
        }}
      >
        {crypto.address}
      </Typography.Text>

      <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
        Scan the QR code or copy the address above
      </Typography.Text>
    </Flex>
  );
};
