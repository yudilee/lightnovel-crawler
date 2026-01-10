import { HeartOutlined } from '@ant-design/icons';
import { Button } from 'antd';

export const DonateButton = () => {
  return (
    <Button
      block
      type="primary"
      target="_blank"
      rel="noopener noreferrer"
      href="https://paypal.me/bitan0n"
      icon={<HeartOutlined twoToneColor="red" />}
    >
      Donate
    </Button>
  );
};
