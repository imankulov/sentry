import React from "react";
var PureRenderMixin = require('react/addons').addons.PureRenderMixin;

var MutedBox = React.createClass({
  mixins: [PureRenderMixin],

  render() {
    if (this.props.status !== 'muted') {
      return null;
    }
    return (
      <div className="alert alert-info alert-block">
        This event has been muted. You will not be notified of any changes and it will not show up in the default feed.
      </div>
    );
  }
});

export default MutedBox;

