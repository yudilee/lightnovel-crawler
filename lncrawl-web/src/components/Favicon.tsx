import { API_BASE_URL } from '@/config';
import { Auth } from '@/store/_auth';
import { Avatar, type AvatarProps } from 'antd';
import qs from 'qs';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';

export const Favicon: React.FC<
  Omit<AvatarProps, 'src'> & {
    url: string;
  }
> = ({ url, ...props }) => {
  const token = useSelector(Auth.select.authToken);

  const faviconLink = useMemo(() => {
    if (!url) return null;
    const search = qs.stringify({ url, token });
    return `${API_BASE_URL}/api/meta/favicon?${search}`;
  }, [url, token]);

  return <Avatar size={24} {...props} src={faviconLink} />;
};
