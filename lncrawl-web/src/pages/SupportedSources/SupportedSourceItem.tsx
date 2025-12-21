import { Favicon } from '@/components/Favicon';
import type { SourceItem } from '@/types';
import { FlagFilled, GlobalOutlined, StopOutlined } from '@ant-design/icons';
import { Card, Flex, Tag, Typography } from 'antd';
import { useInView } from 'react-intersection-observer';
import { SourceFeatureIcons } from './SourceFeatureIcons';

export const SupportedSourceItem: React.FC<{
  source: SourceItem;
  disabled?: boolean;
}> = ({ source, disabled }) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '5px',
  });

  return (
    <Card
      ref={ref}
      size="small"
      hoverable={!disabled}
      style={{ opacity: disabled ? 0.8 : 1 }}
    >
      <Flex align="center" gap={15}>
        {inView && (
          <Favicon
            url={source.url}
            style={{ backgroundColor: '#39f' }}
            icon={disabled ? <StopOutlined /> : <GlobalOutlined />}
          />
        )}
        <Flex vertical style={{ flex: 1 }}>
          <Typography.Link
            strong
            delete={disabled}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {source.url}
          </Typography.Link>
          {disabled && source.disable_reason && (
            <Typography.Text type="secondary">
              {source.disable_reason}
            </Typography.Text>
          )}
        </Flex>
        {source.language && (
          <Flex wrap align="center" gap="7px">
            <SourceFeatureIcons source={source} />
            <Tag icon={<FlagFilled />}>{source.language.toUpperCase()}</Tag>
          </Flex>
        )}
      </Flex>
    </Card>
  );
};
