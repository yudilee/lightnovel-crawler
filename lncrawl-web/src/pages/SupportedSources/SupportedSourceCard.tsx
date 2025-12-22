import { Favicon } from '@/components/Favicon';
import type { SourceItem } from '@/types';
import { getGradientForId } from '@/utils/gradients';
import { formatDate, parseDate } from '@/utils/time';
import {
  FlagOutlined,
  GlobalOutlined,
  LoginOutlined,
  PictureOutlined,
  SearchOutlined,
  StopOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Card, Flex, Space, Tag, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { getLanguageLabel } from './utils';

export const SupportedSourceCard: React.FC<{
  source: SourceItem;
  disabled?: boolean;
}> = ({ source, disabled }) => {
  const updatedAt = formatDate(parseDate(Number(source.version) * 1000));

  return (
    <Card size="small" style={{ opacity: disabled ? 0.8 : 1 }}>
      <Space size={15} style={{ width: '100%' }}>
        <Favicon
          size="large"
          url={source.url}
          style={{ background: getGradientForId(source.url) }}
          icon={disabled ? <StopOutlined /> : <GlobalOutlined />}
        />

        <Flex vertical>
          <Typography.Link
            strong
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ margin: 0, fontSize: 16 }}
          >
            {source.url}
          </Typography.Link>

          {disabled && source.disable_reason ? (
            <Typography.Text type="secondary" italic>
              {source.disable_reason}
            </Typography.Text>
          ) : source.total_novels > 0 ? (
            <Typography.Text type="secondary" italic>
              Found{' '}
              <Link type="secondary" to={`/novels?domain=${source.domain}`}>
                {source.total_novels} novel{source.total_novels > 1 && 's'}
              </Link>{' '}
              using this source
            </Typography.Text>
          ) : null}

          <Flex gap={7} align="center" wrap style={{ marginTop: 8 }}>
            {Boolean(source.version && updatedAt) && (
              <Tag color="cyan" icon={'Version: '} title="Updated At">
                {updatedAt}
              </Tag>
            )}
            {Boolean(source.language) && (
              <Tag icon={<FlagOutlined />} title="Language" color="green">
                {getLanguageLabel(source.language)}
              </Tag>
            )}
            {Boolean(source.has_manga) && (
              <Tag icon={<PictureOutlined />}>Has Manga</Tag>
            )}
            {Boolean(source.has_mtl) && (
              <Tag icon={<TranslationOutlined />}>Has MTL</Tag>
            )}
            {Boolean(source.can_login) && (
              <Tag icon={<LoginOutlined />}>Can Login</Tag>
            )}
            {Boolean(source.can_search) && (
              <Tag icon={<SearchOutlined />}>Can Search</Tag>
            )}
            {source.total_commits > 0 && (
              <Tag title="Total Commits" color="processing">
                {source.total_commits} commit
                {source.total_commits > 1 ? 's' : ''}
              </Tag>
            )}
          </Flex>
        </Flex>
      </Space>
    </Card>
  );
};
