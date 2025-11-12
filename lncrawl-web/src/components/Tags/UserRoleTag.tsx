import { UserRole } from '@/types';
import { Tag } from 'antd';

export const UserRoleTag: React.FC<{ value?: UserRole }> = ({ value }) => {
  if (!value) return null;
  return (
    <Tag color={value === 'admin' ? 'red' : 'blue'}>{value.toUpperCase()}</Tag>
  );
};
