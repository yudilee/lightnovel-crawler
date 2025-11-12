import { Tag } from 'antd';

export const UserStatusTag: React.FC<{ value?: boolean }> = ({ value }) => {
  return (
    <Tag color={value ? 'green' : 'cyan'}>{value ? 'Active' : 'Inactive'}</Tag>
  );
};
