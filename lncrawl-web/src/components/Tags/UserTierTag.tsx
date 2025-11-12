import { UserTier } from '@/types';
import { CrownFilled, SmileOutlined, StarFilled } from '@ant-design/icons';
import { Tag } from 'antd';

export const UserTierTag: React.FC<{ value?: UserTier }> = ({ value }) => {
  switch (value) {
    case UserTier.BASIC:
      return <Tag icon={<SmileOutlined />}>Basic</Tag>;
    case UserTier.PREMIUM:
      return (
        <Tag color="gold" icon={<StarFilled />}>
          Premium
        </Tag>
      );
    case UserTier.VIP:
      return (
        <Tag bordered color="volcano-inverse" icon={<CrownFilled />}>
          VIP
        </Tag>
      );
    default:
      return null;
  }
};
